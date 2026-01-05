# Release Instructions for Testing Update System

## Step 1: Release Version 1.9.0

1. **Build the executable:**
   ```bash
   .\build.bat
   ```

2. **Create a GitHub Release:**
   - Go to: https://github.com/Samer-Ismael/PC-Gaming-App/releases/new
   - **Tag version:** `1.9.0` (or `v1.9.0`)
   - **Release title:** `Version 1.9.0`
   - **Description:** Initial release with modern UI and improved features
   - **Attach file:** Upload `dist\Monitor.exe` as a release asset
   - Click "Publish release"

## Step 2: Update to Version 2.0.0 (for testing)

1. **Update the version in code:**
   - Edit `config.py` and change `APP_VERSION = "1.9.0"` to `APP_VERSION = "2.0.0"`

2. **Rebuild the executable:**
   ```bash
   .\build.bat
   ```

3. **Create another GitHub Release:**
   - Go to: https://github.com/Samer-Ismael/PC-Gaming-App/releases/new
   - **Tag version:** `2.0.0` (or `v2.0.0`)
   - **Release title:** `Version 2.0.0`
   - **Description:** Test update - Modern UI improvements
   - **Attach file:** Upload the new `dist\Monitor.exe` as a release asset
   - Click "Publish release"

## Step 3: Test the Update System

1. **Install version 1.9.0:**
   - Download and run the Monitor.exe from the 1.9.0 release
   - The app should show version 1.9.0

2. **Wait for update check:**
   - The app checks for updates every 15 minutes
   - Or refresh the page to trigger a check

3. **Verify update notification:**
   - After 15 minutes (or on refresh), you should see:
   - Green message: "New version available! Click to update."

4. **Test the update:**
   - Click the update message
   - The app should:
     - Download Monitor.exe from the 2.0.0 release
     - Close the old version
     - Launch the new version
     - Show version 2.0.0

## Important Notes

- **Version format:** The updater accepts versions like `1.9.0`, `2.0.0`, or `v1.9.0`, `v2.0.0`
- **File name:** Make sure the uploaded file is named `Monitor.exe` (or contains "Monitor" in the name)
- **Release order:** Always create releases with increasing version numbers (1.9.0 < 2.0.0)
- **Testing:** After testing, you can delete the test releases if needed

## Troubleshooting

- If update doesn't show: Check that the GitHub release tag version is higher than the current version
- If download fails: Verify the release asset is named correctly and is accessible
- If update fails: Check that Monitor.exe has write permissions in its directory

