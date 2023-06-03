pyinstaller --onefile --noconsole --icon=q2rad.ico --distpath ./bin/macos ./q2radlauncher/q2radlauncher.py
# rm bin/macos/q2radlauncher
# create-dmg \
  # --volname "q2radlauncher Installer" \
  # --volicon "q2rad.ico" \
  # --window-pos 200 120 \
  # --window-size 800 400 \
  # --icon-size 100 \
  # --icon "q2rad.ico" 200 190 \
  # --hide-extension "q2radlauncher.app" \
  # --app-drop-link 600 185 \
  # "bin/macos/q2radlauncher-Installer.dmg" \
  # "bin/macos"
 
#zip bin/macos/q2radlauncher-installer.zip bin/macos/q2radlauncher.app/

rm -r bin/macos/q2radlauncher.app
#zip bin/macos/q2radlauncher-installer.zip bin/macos/q2radlauncher

#rm -r bin/macos/q2radlauncher