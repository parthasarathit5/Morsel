import type { CapacitorConfig } from '@capacitor/cli'

/**
 * Foodiebay Android app configuration.
 *
 * The web build (frontend/dist) is bundled into a native Android WebView app.
 * Build steps:
 *   npm run build            # produces frontend/dist
 *   npx cap sync android     # copies dist + plugins into android/
 *   npx cap open android     # open in Android Studio → Build > APK
 *
 * IMPORTANT: before building the APK, set VITE_API_BASE_URL to your live
 * Render backend URL in frontend/.env.production so the app calls the API
 * instead of the dev proxy.
 */
const config: CapacitorConfig = {
  appId: 'app.Foodiebay.mobile',
  appName: 'Foodiebay',
  webDir: 'dist',
  server: {
    // Allow the WebView to call the hosted API over HTTPS.
    cleartext: false,
    androidScheme: 'https',
  },
}

export default config
