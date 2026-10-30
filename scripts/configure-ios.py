"""Configure the generated Capacitor iOS project for personal sideloading."""

import json
from pathlib import Path
import plistlib

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "ios/App/App"


def configure():
    info_path = APP / "Info.plist"
    with info_path.open("rb") as stream:
        info = plistlib.load(stream)
    info.update({
        "CFBundleDevelopmentRegion": "zh_CN",
        "UIFileSharingEnabled": True,
        "LSSupportsOpeningDocumentsInPlace": True,
        "UIRequiredDeviceCapabilities": ["arm64"],
    })
    with info_path.open("wb") as stream:
        plistlib.dump(info, stream, sort_keys=False)

    privacy = {
        "NSPrivacyTracking": False,
        "NSPrivacyCollectedDataTypes": [],
        "NSPrivacyAccessedAPITypes": [{
            "NSPrivacyAccessedAPIType": "NSPrivacyAccessedAPICategoryFileTimestamp",
            "NSPrivacyAccessedAPITypeReasons": ["C617.1"],
        }],
    }
    with (APP / "PrivacyInfo.xcprivacy").open("wb") as stream:
        plistlib.dump(privacy, stream)

    project_path = ROOT / "ios/App/App.xcodeproj/project.pbxproj"
    project = project_path.read_text(encoding="utf-8")
    if "PrivacyInfo.xcprivacy in Resources" not in project:
        replacements = {
            "/* Begin PBXBuildFile section */":
                "/* Begin PBXBuildFile section */\n"
                "\t\tC0DE00000000000000000001 /* PrivacyInfo.xcprivacy in Resources */ = "
                "{isa = PBXBuildFile; fileRef = C0DE00000000000000000002 /* PrivacyInfo.xcprivacy */; };",
            "/* Begin PBXFileReference section */":
                "/* Begin PBXFileReference section */\n"
                "\t\tC0DE00000000000000000002 /* PrivacyInfo.xcprivacy */ = "
                '{isa = PBXFileReference; lastKnownFileType = text.xml; path = PrivacyInfo.xcprivacy; sourceTree = "<group>"; };',
            "\t\t\t\t504EC3131FED79650016851F /* Info.plist */,":
                "\t\t\t\t504EC3131FED79650016851F /* Info.plist */,\n"
                "\t\t\t\tC0DE00000000000000000002 /* PrivacyInfo.xcprivacy */,",
            "\t\t\t\t504EC3121FED79650016851F /* LaunchScreen.storyboard in Resources */,":
                "\t\t\t\t504EC3121FED79650016851F /* LaunchScreen.storyboard in Resources */,\n"
                "\t\t\t\tC0DE00000000000000000001 /* PrivacyInfo.xcprivacy in Resources */,",
        }
        for before, after in replacements.items():
            if project.count(before) != 1:
                raise RuntimeError("Capacitor Xcode template changed; review privacy resource wiring")
            project = project.replace(before, after)
        project_path.write_text(project, encoding="utf-8", newline="\n")

    version = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    print(f"iOS {version}: document sharing and privacy manifest configured")


if __name__ == "__main__":
    configure()
