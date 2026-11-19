Name:		hashmap-util
Version:	2.0.0
Release:	1
Summary:	Weak hash maps with pluggable equality
Group:		Development/Java
License:	MIT
URL:		https://github.com/plume-lib/hashmap-util
# Tag v2.0.0. The Gradle wrapper jar is removed.
# 0.0.1 stays because published packages still require that coordinate.
Source0:	https://github.com/plume-lib/hashmap-util/archive/refs/tags/v%{version}.tar.gz#/hashmap-util-%{version}.tar.gz
Source1:	https://github.com/plume-lib/hashmap-util/archive/refs/tags/v0.0.1.tar.gz#/hashmap-util-0.0.1.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(org.checkerframework:checker-qual) = 4.4.0
Requires:	mvn(org.checkerframework:checker-qual) = 4.4.0

%description
org.plumelib:hashmap-util %{version} provides WeakIdentityHashMap,
WeakHasherMap, and Hasher. plume-util %{version} compiles against this
jar. 0.0.1 stays installed for packages that still require it. The
public classes keep the same names. They do not reference reflection-util.

%prep
%autosetup -n hashmap-util-%{version} -p1
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries.list
if [ -s binaries.list ]; then
	cat binaries.list
	exit 1
fi
test -f src/main/java/org/plumelib/util/WeakIdentityHashMap.java
tar -C %{_builddir} -xf %{SOURCE1}
find %{_builddir}/hashmap-util-0.0.1 -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries-old.list
if [ -s binaries-old.list ]; then
	cat binaries-old.list
	exit 1
fi
test -f %{_builddir}/hashmap-util-0.0.1/src/main/java/org/plumelib/util/Hasher.java

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
build_old() (
	cd "%{_builddir}/hashmap-util-0.0.1"
	find src/main/java -name '*.java' ! -name 'package-info.java' ! -name 'module-info.java' > sources.list
	test "$(wc -l < sources.list)" -eq 3
	mkdir -p classes
	javac --release 8 -encoding UTF-8 -Xlint:-options -proc:none \
		-cp %{_javadir}/checker-qual.jar \
		-d classes @sources.list
	jar cf hashmap-util.jar -C classes .
	jar i hashmap-util.jar
	jar tf hashmap-util.jar | grep -E '\.(java|jar|so|node|wasm)$' && exit 1 || true
	javap -verbose -cp hashmap-util.jar org.plumelib.util.WeakIdentityHashMap | grep -F -q 'major version: 52'
	cat > hashmap-util.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.plumelib</groupId>
  <artifactId>hashmap-util</artifactId>
  <version>0.0.1</version>
  <name>Plume-lib HashMap Util</name>
  <description>Weak hash maps with pluggable equality.</description>
  <licenses>
    <license>
      <name>MIT License</name>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.checkerframework</groupId>
      <artifactId>checker-qual</artifactId>
      <version>4.4.0</version>
    </dependency>
  </dependencies>
</project>
EOF
)
build_new() (
	cd "%{_builddir}/hashmap-util-%{version}"
	find src/main/java -name '*.java' ! -name 'module-info.java' > sources.list
	test "$(wc -l < sources.list)" -eq 4
	mkdir -p classes
	javac --release 17 -encoding UTF-8 -Xlint:-options -proc:none \
		-cp %{_javadir}/checker-qual.jar \
		-d classes @sources.list
	jar cf hashmap-util.jar -C classes .
	jar i hashmap-util.jar
	jar tf hashmap-util.jar | grep -E '\.(java|jar|so|node|wasm)$' && exit 1 || true
	javap -verbose -cp hashmap-util.jar org.plumelib.util.WeakIdentityHashMap | grep -F -q 'major version: 61'
	cat > hashmap-util.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.plumelib</groupId>
  <artifactId>hashmap-util</artifactId>
  <version>2.0.0</version>
  <name>Plume-lib HashMap Util</name>
  <description>Weak hash maps with pluggable equality.</description>
  <licenses>
    <license>
      <name>MIT License</name>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.checkerframework</groupId>
      <artifactId>checker-qual</artifactId>
      <version>4.4.0</version>
    </dependency>
  </dependencies>
</project>
EOF
	grep -F -q '<version>2.0.0</version>' hashmap-util.pom
)
build_old
build_new

%install
set -eo pipefail
old="%{_builddir}/hashmap-util-0.0.1"
sysjar install --buildroot %{buildroot} \
	--artifact "${old}/hashmap-util.pom:${old}/hashmap-util.jar" \
	--file-name hashmap-util-0.0.1 \
	--filelist .mfiles-old
index="%{buildroot}/usr/share/sysjar/index/org.plumelib/hashmap-util.sysjar"
test -f "$index"
/bin/mv "$index" "%{buildroot}/usr/share/sysjar/index/org.plumelib/hashmap-util-0.0.1.sysjar"
sed -i 's|/usr/share/sysjar/index/org\.plumelib/hashmap-util\.sysjar|/usr/share/sysjar/index/org.plumelib/hashmap-util-0.0.1.sysjar|' .mfiles-old
idx="%{buildroot}/usr/share/sysjar/index/org.plumelib/hashmap-util-0.0.1.sysjar"
grep -F -q '"version": "0.0.1"' "$idx"
grep -F -q '"artifactId": "hashmap-util"' "$idx"
new="%{_builddir}/hashmap-util-%{version}"
sysjar install --buildroot %{buildroot} \
	--artifact "${new}/hashmap-util.pom:${new}/hashmap-util.jar" \
	--file-name hashmap-util \
	--filelist .mfiles-new
idxn="%{buildroot}/usr/share/sysjar/index/org.plumelib/hashmap-util.sysjar"
grep -F -q '"version": "%{version}"' "$idxn"
grep -F -q '"artifactId": "hashmap-util"' "$idxn"
test -s %{buildroot}%{_javadir}/hashmap-util-0.0.1.jar
test -s %{buildroot}%{_javadir}/hashmap-util.jar
: > .mfiles
for list in .mfiles-old .mfiles-new
do
	while IFS= read -r line; do
		grep -qxF -- "$line" .mfiles || printf '%%s\n' "$line" >> .mfiles
	done < "$list"
done
grep -F -q '/hashmap-util.jar' .mfiles
grep -F -q '/hashmap-util-0.0.1.jar' .mfiles

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
mkdir -p check
cat > check/Smoke.java << 'END'
import org.plumelib.util.WeakIdentityHashMap;
public class Smoke {
	public static void main(String[] args) {
		WeakIdentityHashMap<String, String> map = new WeakIdentityHashMap<>();
		String key = new String("k");
		map.put(key, "v");
		String got = map.get(key);
		if (!"v".equals(got) || map.size() != 1) {
			throw new RuntimeException(got + " " + map.size());
		}
		System.out.println("hashmap_ok " + args[0] + " " + got + " " + map.size());
	}
}
END
QUAL=%{_javadir}/checker-qual.jar
NEW=%{buildroot}%{_javadir}/hashmap-util.jar
OLD=%{buildroot}%{_javadir}/hashmap-util-0.0.1.jar
javac --release 8 -encoding UTF-8 -Xlint:-options -proc:none -cp "$NEW:$QUAL" -d check check/Smoke.java
java -cp "check:$NEW:$QUAL" Smoke %{version} > check/new.txt
java -cp "check:$OLD:$QUAL" Smoke 0.0.1 > check/old.txt
cat check/new.txt check/old.txt
grep -F -q 'hashmap_ok %{version} v 1' check/new.txt
grep -F -q 'hashmap_ok 0.0.1 v 1' check/old.txt

%files -f .mfiles
%doc LICENSE README.md
