# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

Name:           xml-commons-apis
Summary:        APIs for DOM, SAX, and JAXP
Version:        1.3.04
Release:        3.6%{?dist}
Epoch:          0
License:        ASL 2.0 and W3C and Public Domain
URL:            http://xml.apache.org/commons/
Source0:        xml-commons-external-1.3.04-src.tar.gz
# svn export http://svn.apache.org/repos/asf/xml/commons/tags/xml-commons-external-1_3_04/java/external/
# tar czf xml-commons-external-1.3.04-src.tar.gz external
Source1:        %{name}-MANIFEST.MF
Source2:        %{name}-ext-MANIFEST.MF
Requires:       jpackage-utils >= 0:1.5
BuildRequires:  jpackage-utils >= 0:1.5
BuildRequires:  ant
Group:          Text Processing/Markup/XML
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%if ! %{gcj_support}
BuildArch:      noarch
%endif

Obsoletes:      xml-commons <= 0:1.3.02
Provides:       xml-commons = %{epoch}:%{version}-%{release}

Provides:       jaxp = 1.3
Provides:       xml-commons-jaxp-1.3-apis = %{epoch}:%{version}-%{release}

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
Requires(post):         java-gcj-compat
Requires(postun):       java-gcj-compat
%endif

%description
xml-commons-apis is designed to organize and have common packaging for
the various externally-defined standard interfaces for XML. This
includes the DOM, SAX, and JAXP. 

%package manual
Summary:        Manual for %{name}
Group:          Text Processing/Markup/XML

%description manual
Manual for %{name}.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Documentation
# for /bin/rm and /bin/ln
Requires(post): coreutils
Requires(postun): coreutils

%description javadoc
Javadoc for %{name}.

# -----------------------------------------------------------------------------

%prep
%setup -q -n external

# remove all binary libs and prebuilt javadocs
rm -rf `find . -name "*.jar" -o -name "*.gz"`
rm -rf build  

# -----------------------------------------------------------------------------

%build
export OPT_JAR_LIST="./external/build/xml-apis.jar"
ant jar javadoc

# -----------------------------------------------------------------------------

%install
rm -rf $RPM_BUILD_ROOT

# inject OSGi manifests
mkdir -p META-INF
cp -p %{SOURCE1} META-INF/MANIFEST.MF
touch META-INF/MANIFEST.MF
zip -u build/xml-apis.jar META-INF/MANIFEST.MF
cp -p %{SOURCE2} META-INF/MANIFEST.MF
touch META-INF/MANIFEST.MF
zip -u build/xml-apis-ext.jar META-INF/MANIFEST.MF

# Jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}
cp -p build/xml-apis.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
cp -p build/xml-apis-ext.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-ext-%{version}.jar

# Jar versioning
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in %{name}-%{version}.jar; do ln -sf ${jar} dom3-${jar}; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)
# for better interoperability with the jpp apis packages
ln -sf %{name}.jar ${RPM_BUILD_ROOT}%{_javadir}/jaxp13.jar
ln -sf %{name}.jar ${RPM_BUILD_ROOT}%{_javadir}/jaxp.jar
ln -sf %{name}.jar ${RPM_BUILD_ROOT}%{_javadir}/xml-commons-jaxp-1.3-apis.jar

# Javadocs
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr build/docs/javadoc/* \
  $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} 

# prevent apis javadoc from being included in doc
rm -rf docs/javadoc

# -----------------------------------------------------------------------------

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

# -----------------------------------------------------------------------------

%if %{gcj_support}
%post
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%if %{gcj_support}
%postun
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%files
%defattr(0644,root,root,0755)
%doc LICENSE NOTICE 
%doc LICENSE.dom-documentation.txt README.dom.txt
%doc LICENSE.dom-software.txt
%doc LICENSE.sax.txt README-sax  README.sax.txt
%{_javadir}/*

%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}-%{version}.jar.*
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}-ext-%{version}.jar.*
%endif

%files manual
%defattr(0644,root,root,0755)
%doc build/docs/*

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/*

# -----------------------------------------------------------------------------

%changelog
* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0:1.3.04-3.6
- Rebuilt for RHEL 6

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.3.04-3.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.3.04-2.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 6 2009 Alexander Kurtakov <akurtako@redhat.com> 0:1.3.04-1.5
- Add osgi metadata to the ext jar too.

* Fri Jan 30 2009 Alexander Kurtakov <akurtako@redhat.com> 0:1.3.04-1.4
- Add osgi metadata.

* Fri Sep 19 2008 Matt Wringe <mwringe@redhat.com> - 0:1.3.04-1.3
- Remove natively compiled bits from the javadoc package (462809)

* Thu Jul 10 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.3.04-1.2
- drop repotag
- fix license tag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:1.3.04-1jpp.1
- Autorebuild for GCC 4.3

* Tue Mar 06 2007 Matt Wringe <mwringe@redhat.com> - 0:1.3.04-0jpp.1
- Update to 1.3.04

* Tue Mar 06 2007 Matt Wringe <mwringe@redhat.com> - 0:1.3.03-0jpp.1
- Split xml-commons package up into 2 separate package: xml-commons-apis
  and xml-commons-which.

* Mon Aug 21 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.3.02-0.b2.7jpp.10
- Add missing Requires for post and postun javadoc sections

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 0:1.3.02-0.b2.7jpp_9fc
- Rebuilt

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0:1.3.02-0.b2.7jpp_8fc
- rebuild

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 0:1.3.02-0.b2.7jpp_7fc
- stop scriptlet spew

* Wed Feb 22 2006 Rafael Schloming <rafaels@redhat.com> - 0:1.3.02-0.b2.7jpp_6fc
- Updated to 1.3

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0:1.0-0.b2.7jpp_5fc
- bump again for double-long bug on ppc(64)

* Wed Dec 21 2005 Jesse Keating <jkeating@redhat.com> 0:1.0-0.b2.7jpp_4fc
- rebuilt again

* Tue Dec 13 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt for new gcj

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Jul 15 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.7jpp_3fc
- Build on ia64, ppc64, s390 and s390x.
- Switch to aot-compile-rpm (also BC-compiles the which jar).

* Wed Jun 15 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.7jpp_2fc
- Remove all prebuilt stuff from the tarball.

* Thu May 26 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.7jpp_1fc
- Upgrade to 1.0-0.b2.7jpp.
- Remove now-unnecessary workaround for #130162.
- Rearrange how BC-compiled stuff is built and installed.

* Mon May 23 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.6jpp_13fc
- Add alpha to the list of build architectures (#157522).
- Use absolute paths for rebuild-gcj-db.

* Thu May  5 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.6jpp_12fc
- Add dependencies for %%post and %%postun scriptlets (#156901).

* Tue May  3 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.6jpp_11fc
- BC-compile the API jar.

* Tue Apr 26 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.6jpp_10fc
- Remove gcj endorsed dir support (#155693).

* Mon Apr 25 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.6jpp_9fc
- Provide a default transformer when running under libgcj.

* Mon Apr 25 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.6jpp_8fc
- Provide a default DOM builder when running under libgcj (#155693).

* Fri Apr 22 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.6jpp_7fc
- Provide a default SAX parser when running under libgcj (#155693).

* Thu Apr 21 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.6jpp_6fc
- Add gcj endorsed dir support.

* Tue Jan 11 2005 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.6jpp_5fc
- Sync with RHAPS.

* Thu Nov  4 2004 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.6jpp_4fc
- Build into Fedora.

* Thu Oct 28 2004 Gary Benson <gbenson@redhat.com> - 0:1.0-0.b2.6jpp_3fc
- Bootstrap into Fedora.

* Fri Oct 1 2004 Andrew Overholt <overholt@redhat.com> - 0:1.0-0.b2.6jpp_3rh
- add coreutils BuildRequires

* Thu Mar  4 2004 Frank Ch. Eigler <fche@redhat.com> - 0:1.0-0.b2.6jpp_2rh
- RH vacuuming part II

* Tue Mar  2 2004 Frank Ch. Eigler <fche@redhat.com> - 0:1.0-0.b2.6jpp_1rh
- RH vacuuming

* Thu Aug 26 2003 Ralph Apel <r.apel at r-apel.de> - 0:1.0-0.b2.7jpp
- Build with ant-1.6.2

* Mon May  5 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.0-0.b2.6jpp
- Fix non-versioned javadoc symlinking.

* Mon Apr 21 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.0-0.b2.5jpp
- Fix xml-which script.
- Include non-versioned javadoc symlinks.
- Add Epoch: 0.
- Fix jpackage-utils dependency versions.

* Thu Mar 13 2003 Nicolas Mailhot <Nicolas.Mailhot at jpackage.org> - 1.0-0.b2.4jpp
- For jpackage-utils 1.5

* Wed Nov 13 2002 Ville Skyttä <ville.skytta at iki.fi> - 1.0-0.b2.3jpp
- Following upstream changes, resolver is now built from its own package.

* Sun Nov  3 2002 Ville Skyttä <ville.skytta at iki.fi> 1.0-0.b2.2jpp
- Split resolver into its own subpackage.
- Fix Group, Vendor and Distribution tags.
- Use sed instead of bash 2 extension when symlinking jars.
- Add resolver and which shell scripts.

* Thu Jul 11 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-0.b2.1jpp
- 1.0.b2
- get tarball from xml.apache.org
- add macro section

* Fri Jan 18 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 1.0-0.b1.1jpp
- first jpp release
