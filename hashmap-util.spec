Name:		hashmap-util
Version:	0.0.1
Release:	1
Summary:	Weak hash maps with pluggable equality
Group:		Development/Java
License:	MIT
URL:		https://github.com/plume-lib/hashmap-util
# Tag v0.0.1 with the Gradle wrapper jar removed.
Source0:	https://github.com/plume-lib/hashmap-util/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(org.checkerframework:checker-qual) = 4.4.0
Requires:	mvn(org.checkerframework:checker-qual) = 4.4.0

%description
org.plumelib:hashmap-util provides WeakIdentityHashMap and WeakHasherMap.
plume-util 1.8.1 compiles against this jar. The three classes do not
reference reflection-util, so this package does not require it.

%prep
%autosetup -n %{name}-%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
# package-info.java declares org.plumelib.util.hashmap, which is not its directory.
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

%install
sysjar install --buildroot %{buildroot} \
	--artifact hashmap-util.pom:hashmap-util.jar \
	--file-name hashmap-util \
	--filelist .mfiles

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
		System.out.println("hashmap_ok " + got + " " + map.size());
	}
}
END
QUAL=%{_javadir}/checker-qual.jar
JAR=%{buildroot}%{_javadir}/hashmap-util.jar
test -f "$QUAL"
test -f "$JAR"
javac --release 8 -encoding UTF-8 -Xlint:-options -proc:none -cp "$JAR:$QUAL" -d check check/Smoke.java
java -cp "check:$JAR:$QUAL" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'hashmap_ok v 1' check/out.txt

%files -f .mfiles
%doc LICENSE README.md
