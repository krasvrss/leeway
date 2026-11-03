# Leeway for Android

Marine wind and fishing app for Červar Porat, Poreč, Tarska uvala and Novigrad.

Each time it opens, the app downloads a fresh 7-day forecast from Open-Meteo (wind, gusts, waves, sea level, sea and air temperature, cloud and rain). It keeps the last good download, so it still works offline.

What's inside:
- **Three languages:** English, Slovenščina and Hrvatski, picked from the menu at the top right. The app remembers your choice.
- **Fish zones from Poreč and Funtana to Červar, Tarska uvala and Novigrad** for 14 species, rated by tide stage and time of day:
  - Predators: seabass, bluefish, leerfish, dentex, bonito, gof (amberjack), garfish.
  - Bream and bottom fish: orada, fratar, špar, ribon, hake.
  - Squid and cuttlefish.
- **Chart view**: black water, depth lines every metre, blue shallows and seamarks from OpenStreetMap (lights, cardinal beacons, marinas, reefs, shellfish beds), with a scale in nautical miles.
- **Seafloor contours** every 2 m, purple shading on steep drop-offs, and a live coordinate readout (degrees and minutes) with depth.
- **Trolling lines** for Poreč, Červar and Tarska–Novigrad, drawn along the depth contours, with bait, lures, speed and rig for each target fish.
- **Fish calendar** for each species, with bait, lure, colour and retrieve picks.
- **Full-screen map:** the button under the zoom buttons hides everything else; **Show controls** brings it back.
- **Named pins:** press and hold on the map (or tap the pin button), name the spot and save. Pins stay on the map with their names; tap one to rename or remove it.
- **Photo catch log.** Photos of the fish and of the lure, size, lure and colour are entered by you. Weather, tide, moon, season and zone are filled in automatically, including weather history for older catches. The log, photos included, stays on the phone.

There are two ways to get the APK. Option 1 needs no software on your computer.

---

## Option 1: Let GitHub build it (no installs)

1. **Make a free account** at https://github.com, then click **New repository**. Name it `leeway`, make it **Private**, and click **Create repository**.
2. **Upload the project.**
   - On the new repository's page, click **uploading an existing file**.
   - Unzip `leeway-android.zip` and drag *everything inside* the `leeway-android` folder onto the page. That includes the hidden `.github` folder.
     - On a Mac, press **Cmd + Shift + .** in Finder to show hidden folders like `.github`.
   - Click **Commit changes**.
3. **Wait for the build.**
   - Open the **Actions** tab. A run called *Build Android APK* starts by itself and takes about 5 minutes.
   - If nothing starts, open **Actions → Build Android APK** and click **Run workflow**.
4. **Download the APK.**
   - When the run shows a green tick, open it.
   - Under **Artifacts**, download **leeway-apk**. It downloads as a zip; unzip it to get `app-debug.apk`.
5. **Install it on your phone.**
   - Copy `app-debug.apk` to the phone, for example by emailing it to yourself or saving it to Google Drive.
   - Tap the file. When Android asks, allow your browser or Files app to **install unknown apps**, then tap **Install**.

**If the `.github` folder didn't upload:**
1. In the repository, click **Add file → Create new file**.
2. Name the file `.github/workflows/build-apk.yml`.
3. Paste in the contents of that file from the zip, then click **Commit changes**.

## Updates

Every time a change is uploaded, GitHub builds a new APK and publishes it under **Releases** with a version number. The first line of the change's description becomes the release note.

- **In the app:** when Android users open Leeway, it checks for a newer release (at most every 3 hours). If there is one, a banner appears with a **Download** button. They tap it, open the file and tap **Install**. The update installs over the old version and keeps the catch log.
- **Link to share:** https://github.com/krasvrss/leeway/releases/latest/download/leeway.apk always gives the newest APK.
- **Email alerts:** anyone with a GitHub account can open the repository and choose **Watch → Custom → Releases**.

The iPhone web app updates itself the next time it's opened.

## iPhone (and any phone): install it as a web app

GitHub can also publish Leeway as a web app. On iPhone you add it to your Home Screen, and it then opens full screen with its own icon. It downloads fresh forecasts each time it opens and keeps working offline with the last ones. You don't need the App Store or an Apple developer account.

1. **Make the repository public.** In your `leeway` repository go to **Settings → General → Danger Zone → Change visibility → Public**. GitHub's free plan only publishes websites from public repositories. The project contains no personal data; your catch log stays on your phone.
2. **Turn on publishing.** Go to **Settings → Pages**, and under **Build and deployment → Source** choose **GitHub Actions**.
3. **Start it.** Open **Actions → Publish web app → Run workflow**. After about a minute the run shows your address, like `https://YOUR-NAME.github.io/leeway/`.
4. **Add it to the iPhone.** Open that address in **Safari**, tap the **Share** button, then **Add to Home Screen**.

Every time you upload changes, both the Android APK and the web app update by themselves.

Want to keep the repository private instead? Go to https://app.netlify.com/drop, sign up for free, and drag the `www` folder onto the page. You get an address to open in Safari and add to the Home Screen the same way.

Notes for the iPhone version:
- The catch log and photos are saved on that phone, separate from the Android app.
- Open it from the Home Screen icon, not a Safari tab, so iOS keeps your log.

## Native iPhone app (needs a Mac)

The `ios` folder is a ready Xcode project. On a Mac with Xcode:

```
npm install
npx cap sync ios
npx cap open ios
```

In Xcode, pick your Apple ID under **Signing & Capabilities**, plug in the iPhone and press **Run**. With a free Apple ID the app runs for 7 days before you need to press Run again. TestFlight or the App Store need the paid Apple Developer Program.

## Option 2: Android Studio

You need Node.js 22 and Android Studio (it includes Java 21 and the Android SDK).

```
npm install
npx cap sync android
npx cap open android
```

Android Studio opens the project. Plug in your phone with USB debugging on and press **Run**. To get a file instead, use **Build → Build App Bundle(s) / APK(s) → Build APK(s)**.

---

## Changing the app

- **App code and design:** `src/leeway.src.html`, including the fish zones, species, calendar and catch log (search for `FISH MODULE`).
- **Translations:** `src/i18n/t*.py` hold every English text with its Croatian and Slovenian version. After editing, run `python3 src/i18n/merge.py`. The app is written in English; `src/i18n.js` swaps in the translation for whatever is on screen.
- **Data files:** `src/data/`.
  - `coast-porec-tar.json`: OpenStreetMap coastline.
  - `depth-tarska.json`: EMODnet depth grid, Poreč to Novigrad.
  - `seamarks.json`: OpenStreetMap lights, beacons, reefs and shellfish beds.
  - `forecast-fallback.json`: a forecast snapshot used only if the very first launch is offline.

After editing, rebuild the web bundle and copy it into the Android project:

```
python3 src/i18n/merge.py
python3 build-www.py
npx cap sync
```

With Option 1, upload the changed files to GitHub and a new APK builds by itself.

## Publishing on Google Play

The APK above is a debug build. It's fine for your own phone and for friends. To publish on Google Play you need:
- a Google Play developer account (one-time fee),
- a signed release build (in Android Studio: **Build → Generate Signed App Bundle**),
- a privacy policy. The app collects no personal data; it only downloads forecasts from Open-Meteo.

## Data and credits

- **Forecasts:** Open-Meteo (https://open-meteo.com), CC BY 4.0.
- **Coastline:** © OpenStreetMap contributors, ODbL.
- **Depth:** EMODnet Bathymetry DTM.
- **Wider coastline:** Natural Earth.

The bluefish zones, daily scores and lure picks are a guide built from depth, tide, light and weather. They are not fish sightings.

Not for navigation.
