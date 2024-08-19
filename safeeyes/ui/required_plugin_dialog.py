#!/usr/bin/env python
# Safe Eyes is a utility to remind you to take break frequently
# to protect your eyes from eye strain.

# Copyright (C) 2016  Gobinath

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""This module creates the RequiredPluginDialog which shows the error for a
required plugin.
"""

import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from safeeyes import utility
from safeeyes.model import PluginDependency
from safeeyes.translations import translate as _

REQUIRED_PLUGIN_DIALOG_GLADE = os.path.join(
    utility.BIN_DIRECTORY, "glade/required_plugin_dialog.glade"
)


@Gtk.Template(filename=REQUIRED_PLUGIN_DIALOG_GLADE)
class RequiredPluginDialog(Gtk.ApplicationWindow):
    """RequiredPluginDialog shows an error when a plugin has required dependencies."""

    __gtype_name__ = "RequiredPluginDialog"

    lbl_header = Gtk.Template.Child()
    lbl_message = Gtk.Template.Child()
    btn_extra_link = Gtk.Template.Child()

    def __init__(
        self, plugin_id, plugin_name, message, on_quit, on_disable_plugin, application
    ):
        super().__init__(application=application)

        self.on_quit = on_quit
        self.on_disable_plugin = on_disable_plugin

        self.lbl_header.set_label(
            _("The required plugin '%s' is missing dependencies!") % _(plugin_name)
        )

        if isinstance(message, PluginDependency):
            self.lbl_message.set_label(_(message.message))
            self.btn_extra_link.set_label(_("Click here for more information"))
            self.btn_extra_link.set_uri(message.link)
            self.btn_extra_link.set_visible(True)
        else:
            self.lbl_message.set_label(_(message))

    def show(self):
        """Show the dialog."""
        self.show_all()

    @Gtk.Template.Callback()
    def on_window_delete(self, *args):
        """Window close event handler."""
        self.destroy()
        self.on_quit()

    @Gtk.Template.Callback()
    def on_close_clicked(self, *args):
        self.destroy()
        self.on_quit()

    @Gtk.Template.Callback()
    def on_disable_plugin_clicked(self, *args):
        self.destroy()
        self.on_disable_plugin()
