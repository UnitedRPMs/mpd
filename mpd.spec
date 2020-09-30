%global  _hardened_build     1
%global _userunitdir /usr/lib/systemd/user/

%global  mpd_user            mpd
%global  mpd_group           %{mpd_user}

%global  mpd_homedir         %{_localstatedir}/lib/mpd
%global  mpd_logdir          %{_localstatedir}/log/mpd
%global  mpd_musicdir        %{mpd_homedir}/music
%global  mpd_playlistsdir    %{mpd_homedir}/playlists
%global  mpd_rundir          /run/mpd

%global  mpd_configfile      %{_sysconfdir}/mpd.conf
%global  mpd_dbfile          %{mpd_homedir}/mpd.db
%global  mpd_logfile         %{mpd_logdir}/mpd.log
%global  mpd_statefile       %{mpd_homedir}/mpdstate
%global  bversion            0.21


%global commit0 56fa7368e8ec4026fd2157b75aa3ba6fbc0889cd
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver .git%{shortcommit0}

Name:           mpd
Epoch:          1
Version:        0.22
Release:        7%{?dist}
Summary:        The Music Player Daemon
License:        GPLv2+
Group:          Applications/Multimedia
URL:            https://www.musicpd.org/

Source0:        https://github.com/MusicPlayerDaemon/MPD/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
# Note that the 0.18.x branch doesn't yet work with Fedora's version of
# libmpcdec which needs updating.
# https://bugzilla.redhat.com/show_bug.cgi?id=1014468
# http://bugs.musicpd.org/view.php?id=3814#bugnotes
Source2:        mpd.logrotate
Source3:        mpd.tmpfiles.d
Source4:	org.musicpd.mpd.metainfo.xml
Patch0:         mpd-0.20.20-mpdconf.patch

BuildRequires:     alsa-lib-devel
BuildRequires:     audiofile-devel
BuildRequires:     autoconf
BuildRequires:     avahi-glib-devel
BuildRequires:     boost-devel
BuildRequires:     bzip2-devel
BuildRequires:     faad2-devel
BuildRequires:     ffmpeg-devel >= 4.1
BuildRequires:     flac-devel
BuildRequires:     jack-audio-connection-kit-devel
BuildRequires:     lame-devel
BuildRequires:     libao-devel
BuildRequires:     libcdio-paranoia-devel
BuildRequires:     libcurl-devel
BuildRequires:     libid3tag-devel
BuildRequires:     libmad-devel
BuildRequires:     libmms-devel
BuildRequires:     libmodplug-devel
BuildRequires:     libgcrypt-devel
BuildRequires:     meson
BuildRequires:     ninja-build
BuildRequires:     clang
BuildRequires:     /usr/bin/sphinx-build

# Need new version with SV8
# BuildRequires:     libmpcdec-devel

BuildRequires:     libogg-devel
BuildRequires:     libsamplerate-devel
BuildRequires:     libshout-devel
BuildRequires:     libvorbis-devel
BuildRequires:     mikmod-devel
BuildRequires:     opus-devel
BuildRequires:     pkgconfig(libpulse)
BuildRequires:     soxr-devel
BuildRequires:     sqlite-devel
BuildRequires:     systemd-devel
BuildRequires:     wavpack-devel
BuildRequires:     yajl-devel
BuildRequires:     zlib-devel
BuildRequires:     zziplib-devel
BuildRequires:     libsidplayfp-devel
BuildRequires:     adplug-devel
BuildRequires:     avahi-compat-libdns_sd-devel
BuildRequires:     avahi-devel
BuildRequires:     dbus-devel
BuildRequires:     expat-devel
BuildRequires:     fluidsynth-devel
BuildRequires:     libmpdclient-devel
BuildRequires:     libnfs-devel
BuildRequires:     libsmbclient-devel
BuildRequires:     libsndfile-devel
BuildRequires:     libupnp-devel
BuildRequires:     mpg123-devel
BuildRequires:     openal-soft-devel
BuildRequires:     twolame-devel
BuildRequires:     wildmidi-devel
BuildRequires:     freetype-devel

Requires(pre):     shadow-utils
Requires(post):    systemd
Requires(preun):   systemd
Requires(postun):  systemd

%description
Music Player Daemon (MPD) is a flexible, powerful, server-side application for
playing music. Through plugins and libraries it can play a variety of sound
files (e.g., OGG, MP3, FLAC, AAC, WAV) and can be controlled remotely via its
network protocol. It can be used as a desktop music player, but is also great
for streaming music to a stereo system over a local network. There are many
GUI and command-line applications to choose from that act as a front-end for
browsing and playing your MPD music collection.


%prep
%autosetup -n MPD-%{commit0} -p1
mkdir -p build
 
%build


_opts=('-Ddocumentation=disabled'
	       '-Dchromaprint=disabled' # appears not to be used for anything
	       '-Dsidplay=disabled' # unclear why but disabled in the past
	       '-Dlibwrap=disabled' # twentieth century's over
	       '-Dadplug=disabled' # not in an official repo
	       '-Dsndio=disabled' # interferes with detection of alsa devices
	       '-Dshine=disabled' # not in an official repo
               '-Dffmpeg=enabled' # We need test if ffmpeg4 is compatible
	)

# Sorry, macros meson doesn't work for us...
%meson --prefix=/usr --libdir=%{_bindir} --libexecdir=%{_libexecdir} --includedir=%{_includedir} --sysconfdir=%{_sysconfdir} --datadir=%{_datadir} --mandir=%{_mandir} --default-library=shared --auto-features auto ${_opts[@]} 

%meson_build

%install


%meson_install

install -p -D -m 0644 %{S:2} \
    %{buildroot}/%{_sysconfdir}/logrotate.d/mpd

install -p -D -m 0644 %{S:3} \
    %{buildroot}/%{_prefix}/lib/tmpfiles.d/mpd.conf

mkdir -p %{buildroot}/run
install -d -m 0755 %{buildroot}/%{mpd_rundir}

mkdir -p %{buildroot}/%{mpd_homedir}
mkdir -p %{buildroot}/%{mpd_logdir}
mkdir -p %{buildroot}/%{mpd_musicdir}
mkdir -p %{buildroot}/%{mpd_playlistsdir}
touch %{buildroot}/%{mpd_dbfile}
touch %{buildroot}/%{mpd_logfile}
touch %{buildroot}/%{mpd_statefile}


#mkdir -p %{buildroot}/%{_sysconfdir} 
install -p -D -m 0644 doc/mpdconf.example %{buildroot}/%{_sysconfdir}/mpd.conf 
#install -m 0644 doc/mpdconf.example %{buildroot}/%{_docdir}/mpd/ 

sed -i -e "s|#music_directory.*$|music_directory \"%{mpd_musicdir}\"|g" \
       -e "s|#playlist_directory.*$|playlist_directory \"%{mpd_playlistsdir}\"|g" \
       -e "s|#db_file.*$|db_file \"%{mpd_dbfile}\"|g" \
       -e "s|#log_file.*$|log_file \"%{mpd_logfile}\"|g" \
       -e "s|#state_file.*$|state_file \"%{mpd_statefile}\"|g" \
       -e 's|#user.*$|user "mpd"|g' \
       %{buildroot}/%{mpd_configfile}
       
# Install AppData
  install -Dm 0644 %{S:4} %{buildroot}/%{_metainfodir}/org.musicpd.mpd.metainfo.xml       

%pre
if [ $1 -eq 1 ]; then
    getent group %{mpd_group} >/dev/null || groupadd -r %{mpd_group}
    getent passwd %{mpd_user} >/dev/null || \
        useradd -r -g %{mpd_group} -d %{mpd_homedir} \
            -s /sbin/nologin -c "Music Player Daemon" %{mpd_user}
    gpasswd -a %{mpd_group} audio || :
    exit 0
fi

%post
%systemd_post mpd.service

%preun
%systemd_preun mpd.service

%postun
%systemd_postun_with_restart mpd.service


%files
%doc AUTHORS COPYING 
%{_bindir}/%{name}
%{_datadir}/icons/hicolor/scalable/apps/mpd.svg
#{_mandir}/man1/mpd.1*
#{_mandir}/man5/mpd.conf.5*
%{_unitdir}/mpd.service
%{_unitdir}/mpd.socket
%{_userunitdir}/mpd.service
%config(noreplace) %{mpd_configfile}
%config(noreplace) %{_sysconfdir}/logrotate.d/mpd
%{_prefix}/lib/tmpfiles.d/mpd.conf
%defattr(-,%{mpd_user},%{mpd_group})
%dir %{mpd_homedir}
%dir %{mpd_logdir}
%dir %{mpd_musicdir}
%dir %{mpd_playlistsdir}
%ghost %dir %{mpd_rundir}
%ghost %{mpd_dbfile}
%ghost %{mpd_logfile}
%ghost %{mpd_statefile}
/usr/lib/systemd/user/mpd.socket
%{_docdir}/mpd/NEWS
%{_docdir}/mpd/README.md
#{_docdir}/mpd/html/
#{_docdir}/mpd/mpdconf.example
%{_metainfodir}/org.musicpd.mpd.metainfo.xml


%changelog

* Mon Sep 28 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.22 
- Updated to 0.22

* Mon Sep 21 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.26-7 
- Updated to 0.21.26

* Thu Jul 09 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.25-7 
- Updated to 0.21.25

* Thu Jun 11 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.24-7 
- Updated to 0.21.24

* Fri Apr 24 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.23-7 
- Updated to 0.21.23

* Fri Apr 10 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.21-8  
- Rebuilt for libcdio

* Thu Mar 19 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.21-7  
- Updated to 0.21.21

* Thu Feb 20 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.20-7  
- Updated to 0.21.20

* Sun Jan 19 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.19-7  
- Updated to 0.21.19

* Thu Jan 9 2020 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.18-7  
- Updated to 0.21.18

* Fri Dec 20 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.17-7  
- Updated to 0.21.17

* Fri Oct 18 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.16-7  
- Updated to 0.21.16

* Fri Sep 27 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.15-7  
- Updated to 0.21.15

* Wed Aug 21 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.14-7  
- Updated to 0.21.14

* Thu Aug 08 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.13-7  
- Updated to 0.21.13

* Wed Jul 03 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.11-7  
- Updated to 0.21.11

* Fri Jun 07 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.10-7  
- Updated to 0.21.10

* Sat May 25 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.9-7  
- Updated to 0.21.9

* Tue Apr 23 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.8-7  
- Updated to 0.21.8

* Wed Apr 10 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.7-7  
- Updated to 0.21.7

* Mon Feb 25 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.5-3  
- Updated to 0.21.5

* Fri Jan 04 2019 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.4-3
- Updated to 0.21.4

* Mon Dec 10 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.3-3
- Rebuilt for ffmpeg

* Fri Nov 16 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.3-2
- Updated to 0.21.3

* Wed Nov 14 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.2-2
- Updated to 0.21.2

* Sun Nov 04 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21.1-2
- Updated to 0.21.1

* Sat Nov 03 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.21-2
- Updated to 0.21
- Changed to meson and clang

* Wed Oct 31 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.23-2
- Updated to 0.20.23

* Mon Oct 22 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.22-2
- Updated to 0.20.22

* Sat Aug 18 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.21-3
- Updated to 0.20.21

* Tue May 22 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.20-3
- Support for various enconders, decoders, storage and others

* Tue May 22 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.20-2
- Updated to 0.20.20

* Thu May 03 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.19-2
- Updated to 0.20.19

* Thu Apr 26 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.18-3  
- Automatic Mass Rebuild

* Mon Feb 26 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.18-2  
- Updated to 0.20.18

* Mon Feb 12 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.17-2  
- Updated to 0.20.17

* Sat Feb 03 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.16-2  
- Updated to 0.20.16

* Sun Jan 07 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.15-2  
- Updated to 0.20.15

* Wed Jan 03 2018 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.14-2  
- Updated to 0.20.14

* Mon Dec 18 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.13-2  
- Updated to 0.20.13

* Tue Nov 28 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.12-2  
- Updated to 0.20.12

* Wed Oct 25 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.11-2  
- Updated to 0.20.11

* Mon Sep 18 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.10-2  
- Updated to 0.20.10

* Mon Jul 31 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.8-2  
- Automatic Mass Rebuild

* Wed May 24 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20.8-1  
- Updated to 0.20.8-1

* Wed Apr 19 2017 Unitedrpms Project <unitedrpms AT protonmail DOT com> 0.20-3  
- Automatic Mass Rebuild

* Sat Mar 18 2017 David Vásquez <davidjeremias82 AT gmail DOT com> - 1:0.20-2
- Rebuilt for libbluray

* Fri Jan 06 2017 Pavlo Rudyi <paulcarroty at riseup.net> 1:0.20-1
- Updated to new release

* Sat Jul 30 2016 Julian Sikorski <belegdol@fedoraproject.org> - 1:0.19.17-3
- Rebuilt for ffmpeg-3.1.1

* Tue Jul 26 2016 leigh scott <leigh123linux@googlemail.com> - 1:0.19.17-2
- Rebuilt for f25 systemd changes
- Disable sidplay (configure fails to find libsidplayfp)

* Mon Jul 25 2016 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 0.19.17-1
- Update to latest upstream release
- Enable sidplay
- Attempt to enable systemd daemon usage

* Tue Jun 21 2016 Nicolas Chauvet <kwizart@gmail.com> - 1:0.19.16-1
- Update to 1.19.16

* Sun Apr 03 2016 Jonathan Dieter <jdieter@gmail.com> 1:0.19.14-1
- Update to latest upstream version
- Remove unneeded systemd service patch (fixed upstream)

* Mon May 04 2015 Ankur Sinha <ankursinha AT fedoraproject DOT org> 1:0.19.9-1
- Update to latest upstream version
- remove conflicts with mpich2 - it doesn't apply any more

* Fri Nov 07 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.19.2-1
- update to upstream release 0.19.2

* Fri Nov 07 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.19.1-2
- fix rpmlint: "non-ghost-in-run /run/mpd"

* Thu Oct 30 2014 Peter Vrabec <pvrabec@gmail.com> - 1:0.19.1-1
- update to upstream release 0.19.1

* Mon Oct 20 2014 Sérgio Basto <sergio@serjux.com> - 1:0.18.16-2
- Rebuilt for FFmpeg 2.4.3

* Sun Oct 05 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.18.16-1
- update to upstream release 0.18.16

* Fri Sep 26 2014 Nicolas Chauvet <kwizart@gmail.com> - 1:0.18.11-3
- Rebuilt for FFmpeg 2.4.x

* Thu Aug 07 2014 Sérgio Basto <sergio@serjux.com> - 1:0.18.11-2
- Rebuilt for ffmpeg-2.3

* Thu Jul 17 2014 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 1:0.18.11-1
- Update to latest upstream release

* Mon May 05 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.18.10-1
- update to upstream release 0.18.10

* Sat Mar 29 2014 Sérgio Basto <sergio@serjux.com> - 1:0.18.9-2
- Rebuilt for ffmpeg-2.2

* Sun Mar 23 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.18.9-1
- update to upstream release 0.18.9
- update URL
- add detached signature as Source1
- add --enable-soundcloud and BR: yajl-devel
- add --enable-pipe-output
- add BR: systemd-devel

* Wed Oct 02 2013 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 1:0.18-0.1.git0e0be02
- Update mpdconf.example patch
- Update to git checkout from master since 0.17 doesn't use new ffmpeg at all
- disable mpcdec support until Fedora package is updated

* Thu Aug 15 2013 Nicolas Chauvet <kwizart@gmail.com> - 1:0.17.3-4
- Rebuilt for FFmpeg 2.0.x

* Sun May 26 2013 Nicolas Chauvet <kwizart@gmail.com> - 1:0.17.3-3
- Rebuilt for x264/FFmpeg

* Sun Feb 24 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.17.3-2
- add tmpfiles.d/mpd.conf in case user wishes to use socket file
- change default socket location in mpd.conf, but leave commented

* Sat Feb 23 2013 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.17.3-1
- update to upstream release 0.17.3
- new CUE parser so remove libcue from BuildRequires
- update systemd scriptlets and remove chkconfig from the Requires
- add a logrotate file

* Sat Nov 24 2012 Nicolas Chauvet <kwizart@gmail.com> - 1:0.16.8-6
- Rebuilt for FFmpeg 1.0

* Fri Aug 17 2012 Adrian Reber <adrian@lisas.de> - 1:0.16.8-5
- fix "mpd fails to bind an addres: started too early" (#2447)

* Tue Jun 26 2012 Nicolas Chauvet <kwizart@gmail.com> - 1:0.16.8-4
- Rebuilt for FFmpeg
- Switch BR to pkgconfig(libpulse)

* Fri May 11 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 0.16.8-3
- enable lastfm support
- enable hardened build
- remove redundant libsidplay-devel BR, as mpd requires libsidplay2

* Mon Apr 09 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 0.16.8-2
- add missing chowns to %%post scriptlet
- add missing %%{mpd_logdir} to %%files

* Mon Apr 09 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.16.8-1
- update to 0.16.8

* Sat Feb 25 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 1:0.16.7-2
- remove obsolete BuildRoot tag, %%clean section and unnecessary macros
- do not add mpd to pulse-rt group as system mode is not recommended by
  pulseaudio upstream, and the group no longer exists
- add triggerun and systemd scriptlets
- add Epoch (for triggerun scriptlet) to allow updates to F16
- change default audio output to pulseaudio

* Sun Feb 05 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 0.16.7-1
- update to 0.16.7

* Sun Jan 08 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 0.16.6-1
- update to 0.16.6
- add convenient global variables
- add systemd unit file instead of initscript
- change incorrect --enable-zip to --enable-zzip
- change default log file location to /var/log/mpd/mpd.log
- remove obsolete mpd error-log
- remove obsolete hal fdi file

* Wed Oct 12 2011 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 0.16.5-1
- Update to latest upstream release (#1954)

* Mon Sep 26 2011 Nicolas Chauvet <kwizart@gmail.com> - 0.15.13-2
- Rebuilt for FFmpeg-0.8

* Thu Oct 28 2010 Adrian Reber <adrian@lisas.de> - 0.15.13-1
- updated to 0.15.13
- added mpd user to audio group (#1461)

* Wed Sep 29 2010 Adrian Reber <adrian@lisas.de> - 0.15.12-1
- updated to 0.15.12

* Tue Jul 20 2010 Adrian Reber <adrian@lisas.de> - 0.15.11-1
- updated to 0.15.11 (#1301)

* Fri Jan 22 2010 Adrian Reber <adrian@lisas.de> - 0.15.8-1
- updated to 0.15.8 (#1042)

* Wed Dec 02 2009 Adrian Reber <adrian@lisas.de> - 0.15.6-1
- updated to 0.15.6 (#989)
- added BR libcue-devel (#930)

* Mon Nov 09 2009 Adrian Reber <adrian@lisas.de> - 0.15.5-1
- updated to 0.15.5 (#929)

* Wed Oct 21 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.15.2-2
- rebuild for new ffmpeg

* Tue Aug 25 2009 Adrian Reber <adrian@lisas.de> - 0.15.2-1
- updated to 0.15.2
- applied patches from David Woodhouse to fix
  "mpd fails to play to usb audio device" (#731)
- fix description (#765)

* Mon Jun 29 2009 Adrian Reber <adrian@lisas.de> - 0.15-1
- updated to 0.15
- added "Conflicts: mpich2" (#593)
- added BR libmms-devel, libmodplug-devel, libsidplay-devel, bzip2-devel
           zziplib-devel, sqlite-devel
- changed BR avahi-devel to avahi-glib-devel
- adapted config file fixups to newest config file layout

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.14.2-2
- rebuild for new F11 features

* Fri Feb 20 2009 Adrian Reber <adrian@lisas.de> - 0.14.2-1
- updated to 0.14.2

* Sat Jan 31 2009 Adrian Reber <adrian@lisas.de> - 0.14-4
- added BR libcurl-devel (#326)

* Sat Dec 27 2008 Adrian Reber <adrian@lisas.de> - 0.14-3
- updated to 0.14 (#229, #280)
- add mpd user to group pulse-rt (#230)
- added BR lame-devel, wavpack-devel, ffmpeg-devel

* Sun Sep 28 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 0.13.2-2
- rebuild

* Fri Jul 25 2008 Adrian Reber <adrian@lisas.de> - 0.13.2-1
- updated to 0.13.2
- added _default_patch_fuzz define

* Thu May 29 2008 Hans de Goede <j.w.r.degoede@hhs.nl> - 0.13.1-3
- Fix mpd crashing when reading in modtracker files (rh bug 448964)

* Thu Mar 06 2008 Adrian Reber <adrian@lisas.de> - 0.13.1-2
- added patches from Thomas Jansen to run mpd by default
  not as root.root but as mpd.mpd

* Mon Feb 11 2008 Adrian Reber <adrian@lisas.de> - 0.13.1-1
- updated to 0.13.1

* Thu Nov 15 2007 Adrian Reber <adrian@lisas.de> - 0.13.0-4
- another rebuilt for faad2

* Fri Nov 09 2007 Thorsten Leemhuis <fedora[AT]leemhuis.info> - 0.13.0-3
- rebuild after faad2 downgrade to fix undefined symbols

* Sat Oct 13 2007 Adrian Reber <adrian@lisas.de> - 0.13.0-2
- rebuilt for rpmfusion
- updated License

* Sun Jul 29 2007 Adrian Reber <adrian@lisas.de> - 0.13.0-1
- update to 0.13.0
- added dwmw2's patches (#1569)
- fixed rpmlint errors and warnings
- added libsamplerate-devel, avahi-devel and
  jack-audio-connection-kit-devel as BR

* Tue Mar 06 2007 Adrian Reber <adrian@lisas.de> - 0.12.1-3
- added flac-1.1.4 patch

* Sat Mar 03 2007 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.12.1-2
- Rebuild

* Mon Nov 27 2006 Adrian Reber <adrian@lisas.de> - 0.12.1-1
- updated to 0.12.1
- added missing Requires
- removed deletion of user mpd during %%preun
- removed -m (create home) from useradd

* Wed Oct 11 2006 Adrian Reber <adrian@lisas.de> - 0.11.6-6
- rebuilt

* Tue Mar 21 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- Add missing BR zlib-devel

* Thu Mar 09 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- switch to new release field

* Mon Mar 06 2006 Thorsten Leemhuis <fedora[AT]livna.org>
- no build time defines anymore so adapt spec completely to livna

* Tue Feb 28 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- add dist

* Sun Nov 28 2004 Aurelien Bompard <gauret[AT]free.fr> 0:0.11.5-0.3
- Apply Adrian Reber's patch to use a system-wide daemon, see bug 2234

* Tue Nov 09 2004 Aurelien Bompard <gauret[AT]free.fr> 0:0.11.5-0.2
- Prepare for FC3 (different BuildRequires)

* Fri Nov 05 2004 Aurelien Bompard <gauret[AT]free.fr> 0:0.11.5-0.fdr.1
- Initial Fedora package (from Mandrake)
