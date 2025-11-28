
Be Safe - Kivy Project
======================

This is a Kivy (Python) prototype of the "Be Safe" emergency app. It includes:
- main.py: core app code
- buildozer.spec: configuration for Buildozer to create an APK

What you asked: I cannot compile the APK inside this chat environment, but I created this project ZIP so you can build it yourself or use GitHub Actions to build it in the cloud.

How to build locally (recommended method - using WSL on Windows or Ubuntu):
1. Install WSL2 or use Ubuntu.
2. Install system packages: openjdk-11-jdk, python3-pip, build-essential, etc.
3. pip3 install --user buildozer cython
4. Ensure ~/.local/bin is in PATH
5. Put this project folder in your home directory and run:
   buildozer -v android debug
6. After the build completes, APK is in bin/ folder.

How to build using GitHub Actions (cloud):
1. Create a new GitHub repo and push this project (including buildozer.spec).
2. Add the .github/workflows/build_apk.yml workflow (I provide it as well).
3. Run the workflow; it will produce a build artifact with the APK (download from Actions UI).

Notes & limitations:
- Camera capture uses the native camera UI (user must take/confirm photo).
- Background / silent capture and guaranteed power-button detection are unreliable on many devices.
- SMS sending may be restricted on some carriers/Android versions.
- For production release, create a signing keystore and sign the release APK.
