use std::time::Instant;

use pyo3;
use pyo3::prelude::{pyclass, pymodule, IntoPyPointer, PyAny, PyModule, PyResult, Python};

use glib::translate::ToGlibPtr;

use wayland_protocols::ext::idle_notify::v1::client::{
    ext_idle_notification_v1::{Event as IdleNotificationV1Event, ExtIdleNotificationV1},
    ext_idle_notifier_v1::ExtIdleNotifierV1,
};

use wayland_client::{
    globals::{registry_queue_init, GlobalListContents},
    protocol::{wl_registry, wl_seat::WlSeat},
    Connection, Dispatch, EventQueue, Proxy, QueueHandle,
};

fn get_gdk_from_py_gdk_wayland_display(
    py: Python<'_>,
    object: &PyAny,
) -> gdk4_wayland::WaylandDisplay {
    let modu = py.import("gi.repository").expect("Failed to import module");
    let gdk_wayland = modu
        .getattr("GdkWayland")
        .expect("Failed to get GdkWayland class");
    let gdk_wayland_display_py = gdk_wayland
        .getattr("WaylandDisplay")
        .expect("Failed to get WaylandDisplay class");
    if !object
        .is_instance(gdk_wayland_display_py)
        .expect("Failed to check if WaylandDisplay")
    {
        panic!("Expected GdkWayland.WaylandDisplay");
    }

    let x = object.into_ptr();
    let x = x.cast::<[*const u8; 4]>();

    // SAFETY: we are relying on implementation details of gobject/gdk_wayland here...
    let x = unsafe { *x };

    let displayptr = x[2];

    // SAFETY: we are relying on implementation details of gobject/gdk_wayland here...
    return unsafe { std::mem::transmute(displayptr) };
}

fn get_connection_from_display(display: &gdk4_wayland::WaylandDisplay) -> Connection {
    // SAFETY: ffi, we have a valid WaylandDisplay instance
    let display_ptr =
        unsafe { gdk4_wayland::ffi::gdk_wayland_display_get_wl_display(display.to_glib_none().0) };

    // SAFETY: we need to make sure that the display_ptr exists as long as backend does
    // this should be the case, as the display is coupled to the gtk application, and we shut down
    // once the app does
    let backend = unsafe {
        wayland_backend::sys::client::Backend::from_foreign_display(display_ptr as *mut _)
    };

    return Connection::from_backend(backend);
}

struct IdleState {
    idle_notification: ExtIdleNotificationV1,
    is_idle: bool,
    is_changed: bool,
    idle_since: Option<Instant>,
}

impl Drop for IdleState {
    fn drop(&mut self) {
        self.idle_notification.destroy();
    }
}

impl IdleState {
    fn new(idle_notification: ExtIdleNotificationV1) -> Self {
        Self {
            idle_notification,
            is_idle: false,
            is_changed: false,
            idle_since: None,
        }
    }

    fn idle(&mut self) {
        self.is_idle = true;
        self.is_changed = true;
        self.idle_since = Some(Instant::now());
    }

    fn resume(&mut self) {
        self.is_idle = false;
        self.is_changed = true;
        self.idle_since = None;
    }

    fn get_idle_time(&self) -> u64 {
        let Some(idle_since) = self.idle_since else {
            return 0;
        };

        return idle_since.elapsed().as_secs();
    }
}

impl Dispatch<wl_registry::WlRegistry, GlobalListContents> for IdleState {
    fn event(
        _: &mut Self,
        _: &wl_registry::WlRegistry,
        _: <wl_registry::WlRegistry as Proxy>::Event,
        _: &GlobalListContents,
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
    }
}

impl Dispatch<WlSeat, ()> for IdleState {
    fn event(
        _: &mut Self,
        _: &WlSeat,
        _: <WlSeat as Proxy>::Event,
        _: &(),
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
    }
}

impl Dispatch<ExtIdleNotifierV1, ()> for IdleState {
    fn event(
        _: &mut Self,
        _: &ExtIdleNotifierV1,
        _: <ExtIdleNotifierV1 as Proxy>::Event,
        _: &(),
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
    }
}

impl Dispatch<ExtIdleNotificationV1, ()> for IdleState {
    fn event(
        state: &mut Self,
        _: &ExtIdleNotificationV1,
        event: <ExtIdleNotificationV1 as Proxy>::Event,
        _: &(),
        _: &Connection,
        _: &QueueHandle<Self>,
    ) {
        if let IdleNotificationV1Event::Idled = event {
            state.idle();
        } else if let IdleNotificationV1Event::Resumed = event {
            state.resume();
        }
    }
}

#[pyclass]
pub struct IdleWatcher {
    _connection: Connection,
    event_queue: EventQueue<IdleState>,
    idle_state: IdleState,
}

#[pyo3::pymethods]
impl IdleWatcher {
    #[new]
    fn new(py: Python<'_>, object: &PyAny) -> Self {
        let display = get_gdk_from_py_gdk_wayland_display(py, object);

        let connection = get_connection_from_display(&display);

        let (globals, event_queue) = registry_queue_init::<IdleState>(&connection).unwrap();

        let mut event_queue = event_queue;

        let queue_handle = event_queue.handle();

        let seat: WlSeat = globals
            .bind(&queue_handle, 1..=WlSeat::interface().version, ())
            .unwrap();

        let ext_idle = globals
            .bind::<ExtIdleNotifierV1, IdleState, ()>(
                &queue_handle,
                1..=ExtIdleNotifierV1::interface().version,
                (),
            )
            .unwrap();

        // this could be more efficient if we were passed in the timeout directly
        let timeout_sec = 1;

        let timeout_msec = timeout_sec * 1000;

        let idle_notification =
            ext_idle.get_idle_notification(timeout_msec, &seat, &queue_handle, ());

        let mut idle_state = IdleState::new(idle_notification);

        event_queue.roundtrip(&mut idle_state).unwrap();

        IdleWatcher {
            _connection: connection,
            event_queue,
            idle_state,
        }
    }

    fn get_idle_time_seconds(&mut self) -> u64 {
        let _ = self
            .event_queue
            .dispatch_pending(&mut self.idle_state)
            .unwrap();
        return self.idle_state.get_idle_time();
    }
}

#[pymodule]
fn rust_wl_bindings(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<IdleWatcher>()?;
    Ok(())
}
