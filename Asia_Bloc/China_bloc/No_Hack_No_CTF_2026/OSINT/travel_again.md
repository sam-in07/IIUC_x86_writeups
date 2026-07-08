# travel again

## Problem Description
- Challenge: `travel again`
- Category: `yochan06`
- Goal: identify the correct coordinates from the challenge image and submit them in NHNC flag format.

## Solution Approach
- This was an OSINT geolocation problem rather than a technical exploitation challenge.
- The decisive clue was not a broad landscape guess but the pair of stone monuments visible in the image.
- Those two monuments were distinctive enough to serve as the main search pivot.
- Once the matching location was found on Google Maps, the remaining work was to read the coordinates and format them exactly as the challenge expected.

## Steps to Derive the Flag
1. Focus on the strongest identifying visual details in the screenshot.
   The important feature was the two stone monuments / markers shown in the image. They were more distinctive than generic scenery, so they provided the best OSINT pivot.

2. Use the monuments as the primary Google-search keywords.
   Search around the monument appearance, arrangement, and any recognizable contextual cues instead of trying to geolocate the entire scene from broad terrain alone.

3. Verify the candidate location in Google Maps.
   After finding the matching place, open it in Google Maps and confirm that the visible monument layout matches the challenge image.

4. Read the latitude and longitude from the map.
   The recovered coordinates were:

   - latitude: `43.1849`
   - longitude: `143.0325`

5. Format the answer exactly as required.
   The challenge wanted coordinates with four digits after the decimal point, wrapped in the NHNC flag format:

```text
NHNC{43.1849,143.0325}
```

## Final Flag
`NHNC{43.1849,143.0325}`