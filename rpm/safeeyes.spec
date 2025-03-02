%global version 2.2.3
%global forgeurl https://github.com/deltragon/SafeEyes
%global commit c28a0ce71803d4ba71c05b976c811d82dd88ce19

%global debug_package %{nil}

Name:           safeeyes
Version:        %{version}
Release:        %autorelease
Summary:        Protect your eyes from eye strain using this continuous breaks reminder

%forgemeta

License:        GPL-3.0-or-later
URL:            %{forgeurl}
Source:         %{forgesource}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  gettext
Requires:       gtk3
#Requires:       libnotify
Requires:       python3dist(babel)
Requires:       python3dist(croniter)
Requires:       python3dist(packaging)
Requires:       python3dist(psutil)
Requires:       python3dist(pygobject)
Requires:       python3dist(python-xlib)
Requires:       python3dist(setuptools)

%description
${summary}


%prep
%forgesetup


%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
# not sure if this is needed - the .mo files are already installed into python3_sitelib
# % find_lang % {name}


%check

%files
%license LICENSE
%doc README.md
%{_bindir}/safeeyes
%{python3_sitelib}/safeeyes
%{python3_sitelib}/safeeyes-%{version}.dist-info
#% {_datarootdir}/applications/safeeyes.desktop


%changelog
%autochangelog

