# **Intro Builder v1.0 — Complete User Manual**

## **Introduction**

Intro Builder is a powerful desktop application for creating professional-quality pre-roll intros for media platforms like Plex and Jellyfin. With an intuitive graphical interface, it lets you combine video/image backgrounds, audio tracks, dynamic text overlays, advanced video effects, and audio processing—all without touching the command line.

The application uses FFmpeg under the hood to render your intros to MP4, WebM, MOV, MKV, or animated GIF formats.

---

## **Getting Started**

### **System Requirements**

- **FFmpeg** (with libx264, libx265, libvpx-vp9, libopus codecs)
- **VLC** (optional, for preview functionality)
- **Python 3.7+** with Tkinter
- **Linux/macOS/Windows** (Linux recommended for stability)

### **Installation**

On Ubuntu/Debian:
```bash
sudo apt install ffmpeg vlc python3-tk
```

### **Launching the Application**

Double-click `Intro_Builder.py` or run it from your system's Python launcher. The application window will open showing a dark-themed interface organized into four tabbed sections.

---

## **The Interface Overview**

The application is organized into five main sections:

1. **Source & Output** — Choose your background and audio files
2. **Text & Overlays** — Add titles, lower thirds, countdowns, and text effects
3. **Video & Colour** — Apply visual effects and color grading
4. **Audio** — Configure audio processing and effects
5. **Quality** — Set compression and encoding quality (shown below Source & Output)

Below all tabs is a permanent **Build Log** panel showing real-time encoding progress, followed by the control buttons at the bottom.

---

## **Section 1: Source & Output**

### **Background File**

Click **BROWSE** next to "Background (video or image)" to select your source media.

**Supported formats:**
- **Video:** .mp4, .mov, .avi, .mkv, .webm
- **Image:** .jpg, .jpeg, .png, .gif (animated or still)

**Examples:**
- Select a 1080p landscape video filmed at 24fps for smooth results
- Select a photo to create a static intro (image will be looped for the duration)
- Select an animated GIF to use as-is with automatic detection

### **Aspect Ratio Preservation**

When you select an **image** file, a checkbox appears: **"Preserve aspect ratio"**

✓ **Checked** (default):
- Image scales to fit 1920×1080 while maintaining its original aspect ratio
- Empty space is padded with a color you choose
- The **Padding colour** selector appears below the checkbox

**Example:** A 16:9 photo stays 16:9; a 4:3 photo gets letterboxed with your chosen color.

✗ **Unchecked**:
- Image is stretched to fill 1920×1080 (may distort)
- No padding color option shown

**Padding Colour Presets:**
- `black`, `white`, `gray`, `#111111`, `#222222`, `#001020`, `#200010`

### **Audio Source – Three Modes**

Choose how to handle audio:

#### **Mode 1: Original Background Track**
- Extracts the audio from your video background
- Used when you have a background video with its own audio
- When you select a video with audio, this is auto-selected
- When you select an image (no audio), this radio button is disabled

**Example:** Upload an MP4 with narration already mixed in; the audio will be reused.

#### **Mode 2: Provided Track**
- Uses a separate audio file that you supply
- A file picker appears to select your audio file
- You can specify a start and end point to trim the audio
- Auto-selected when you pick an audio file

**Supported audio formats:** .mp3, .wav, .m4a, .aac, .flac

**Example:** Record a voiceover as .wav, then upload it separately from your video background.

#### **Mode 3: Silent (No Audio)**
- Creates an intro with no sound
- Useful for silent-mode video feeds
- Auto-selected when you pick an image (images have no audio)

**Example:** Use for a music-free intro that viewers enable their own soundtrack for.

### **Audio Range (Provided Track Only)**

When "Provided track" is selected, two spinners appear:

- **Track Start (s):** Seek point in the audio file (default: 0.0)
- **Track End (s):** Where to stop playback (default: 0.0 = play to end or loop to duration)

**Example:** Your voiceover file is 30 seconds, but you only want seconds 5–8. Set Track Start to `5.0` and Track End to `8.0`. If Track End is 0, the audio plays to its natural end or loops to match your video duration.

### **Duration & Timing**

#### **Duration (s)**

The total length of your output intro in seconds.

- **Default:** 8 seconds
- **Range:** 3–300 seconds
- **Auto-update:** When you select a background video, the duration automatically updates to match the video's length

**Example:** Select a 15-second video background → Duration becomes 15s.

#### **BG Start (s)**

Where to begin playback of the background video (seek position).

**Example:** Your video has a 2-second fade-in you want to skip. Set BG Start to `2.0`.

#### **BG End (s)**

If set to 0 (default), uses the full video duration or loops to match your Duration setting. If you specify a non-zero value, playback stops at that timestamp.

**Example:** Your background video is 30 seconds, but you only want the first 12 seconds. Set BG End to `12.0`.

### **Output Filename**

Enter the name for your final video (without extension).

- **Default:** `intro_output`
- **Output location:** Same directory as the script

**Example:** Type `my_studio_intro` to create `my_studio_intro.mp4` (or .webm, .mkv, etc. depending on format).

### **Output Format**

A dropdown menu to choose your output video codec/container.

**Options:**

| Format | Container | Video Codec | Audio Codec | Best For |
|--------|-----------|------------|------------|----------|
| **mp4_h264_aac** | MP4 | H.264 | AAC | Maximum compatibility, fastest |
| **mp4_h265_aac** | MP4 | H.265 | AAC | Better compression, modern players |
| **webm_vp9_opus** | WebM | VP9 | Opus | Web streaming, high quality |
| **mov_prores** | MOV | ProRes | PCM | Professional editing workflows |
| **mkv_h265_aac** | MKV | H.265 | AAC | Flexible container, best compression |
| **gif_animated** | GIF | Palette | None | Looping social media clips (no audio) |

**Example:** For Plex/Jellyfin, use `mp4_h264_aac`. For archival, use `mkv_h265_aac`.

### **Embed Settings in Output File**

Checkbox: **"Embed settings in output file"** (default: checked)

When enabled, all your current settings (text, effects, timings, etc.) are saved as metadata inside the video file's comment field. Later, you can load the file back and click **[ LOAD SETTINGS FROM FILE ]** to restore all settings—perfect for iterating on the same intro.

**Example:** Build an intro with custom effects, save it. Six months later, load it back to make tweaks without re-entering everything.

---

## **Section 2: Text & Overlays**

### **Overlay Text**

A large text box where you enter the text to display over your intro.

- Supports **multi-line text** — press Enter for new lines
- Text renders line-by-line, centered around the position you choose
- Leave blank to skip text rendering entirely

**Example:**
```
STUDIO PRESENTS
Season 2 • Episode 5
```

### **Font Settings**

#### **Font**
A dropdown listing all available system fonts (sorted alphabetically, excluding @-prefixed fonts).

**Example fonts:**
- `Impact` (bold, eye-catching)
- `Arial` (clean, professional)
- `Courier New` (monospace, technical)

#### **Size**
Font size in pixels.
- **Default:** 180
- **Range:** 10–500

**Example:** For a 1920×1080 frame with two lines of text, 180–240px is typical; 400+ for single large titles.

#### **Colour**
Font color picker with presets.

**Available presets:** `white`, `yellow`, `cyan`, `#ff8844` (orange), `#88ffcc` (mint), `red`, `gold`, `#eeeeee` (off-white)

**Custom colors:** Click the swatch to open a color chooser, or type a hex code directly.

**Example:** White text on dark backgrounds; yellow for high-visibility emergency notices.

#### **Border**
Text outline width in pixels.
- **Default:** 5
- **Range:** 0–30

**Example:** 0 = no outline; 5 = subtle outline; 15 = thick border for contrast.

### **Text Position & Opacity**

#### **Position**
Four options via radio buttons:

- **Center** — Vertically and horizontally centered
- **Top-Center** — Near the top, centered horizontally
- **Bottom-Center** — Near the bottom, centered horizontally
- **Lower-Third** — At the lower-third line (classic broadcast style)

**Example:** Use **Lower-Third** for news intros; **Center** for dramatic reveals.

#### **Opacity %**
Text transparency slider.
- **0%** — Fully transparent (invisible)
- **50%** — Semi-transparent
- **100%** — Fully opaque (default)

**Example:** 70% for subtle watermark-style text that doesn't overpower the background.

### **Text Fade**

A checkbox: **"Text Fade"** — enables gradual fade-in and fade-out animations.

When enabled, four sliders appear:

| Slider | Meaning |
|--------|---------|
| **Fade in after (s)** | Delay before text starts appearing (0 = appear immediately) |
| **Fade in for (s)** | Duration of the fade-in animation |
| **Fade out from (s)** | When fade-out begins (relative to video start) |
| **Fade out for (s)** | Duration of the fade-out animation |

All sliders automatically cap to the video duration.

**Example Scenario:** 8-second intro
- Fade in after: `1.0` (text invisible for first second)
- Fade in for: `1.0` (text gradually appears over the next second)
- Fade out from: `6.0` (text begins disappearing at 6-second mark)
- Fade out for: `1.5` (text is gone by 7.5 seconds)

Result: Text appears at 2s, holds steady from 2–6s, then fades away by 7.5s.

### **Lower Third**

A checkbox: **"Lower Third"** — enables a semi-transparent bar with title and subtitle text.

When checked, additional options appear:

#### **Title & Sub Text**
Two input fields for the main title and subtitle.

**Example:**
- Title: `BREAKING NEWS`
- Sub: `Downtown Community Center`

#### **Display from / to (s)**
When the lower third appears and disappears.

**Example:** 1.0 to 6.0 (appears at 1s, hides at 6s)

#### **Animation**
Two modes:

- **Slide in / slide out** — Bar slides in from the left, holds, then slides out
- **Fade in / fade out** — Bar fades in, holds, then fades out

**Example:** Slide for sports/news; fade for corporate intros.

#### **Box Colour & Opacity**
- **Box colour:** Color picker (presets: black, #222222, #111111, #1a1a2e, #002244, #220011, gray)
- **Box opacity:** Slider from 0–1.0 (0.72 = default 72% opaque)

**Example:** Dark blue (#002244) at 0.6 opacity for a subtle tech-company feel.

### **Countdown Footer**

A checkbox: **"Countdown Footer"** — displays a countdown timer in the video.

The timer shows seconds remaining (e.g., 5, 4, 3, 2, 1) and disappears before reaching 0.

When enabled, four controls appear:

#### **Count from**
How many seconds to count down (typically 5–10).
- **Default:** 5

#### **Font Size**
Size of the countdown numbers.
- **Default:** 100

#### **Colour**
Countdown text color.
- **Presets:** white, yellow, red, cyan

#### **Position**
Where the countdown appears:
- **Bottom-Centre** (default)
- **Bottom-Left**
- **Bottom-Right**
- **Top-Centre**
- **Centre**

**Example Scenario:** 8-second intro with countdown from 5
- Countdown appears at the 3-second mark (8−5=3)
- Shows: **5 4 3 2 1** over the final 5 seconds
- Disappears cleanly before video ends

### **Overlay Extras Opacity**

A master opacity slider for both the lower third AND countdown (if enabled).
- **0%** — Hidden
- **100%** — Full visibility

**Example:** Set to 80% to let the background show through both overlays.

---

## **Section 3: Video & Colour**

### **Video Effects**

A two-column grid of 11 toggle switches, each enabling a visual effect:

#### **Left Column (6 effects)**

**1. Scanline Sweep**
- Animated horizontal light bar sweeps across the frame
- Emulates old CRT monitor scanning
- **Use case:** Retro sci-fi intros

**2. Slow Drift**
- Subtle camera pan from left to right over the duration
- **Use case:** Cinematic, moving backgrounds, parallax effect
- **Conflict:** Incompatible with "Preserve aspect ratio" for images (disables padding)

**3. Mirror Tiles**
- 2×2 kaleidoscope effect (mirrors image in quadrants)
- Very CPU-intensive; uses special processing path
- **Use case:** Psychedelic, trippy intros

**4. Film Grain**
- Analogue noise overlay (film stock texture)
- **Use case:** Vintage, indie, documentary feel

**5. Letterbox**
- Adds black bars top and bottom (2.35:1 cinema aspect ratio)
- **Use case:** Widescreen movie trailer look

**6. Vignette**
- Darkens the edges of the frame, drawing focus to center
- **Use case:** Professional, theatrical presentations

#### **Right Column (5 effects)**

**1. Flash Bar**
- Bright white flash bar appears mid-video
- **Use case:** Action sequences, dramatic reveals

**2. Pulse**
- Rhythmic "breathing" zoom effect
- **Use case:** Energetic, pulsing musical intros

**3. Glitch**
- Digital corruption flicker at multiple points
- **Use case:** Cyberpunk, tech, edgy branding

**4. Bloom**
- Soft glow/bloom on bright areas (combines with bloom shader)
- **Use case:** Dreamy, magical, soft aesthetics

**5. Sharpen**
- Enhances edge detail and crispness
- **Use case:** Technical, crisp, professional look

#### **Reset Video Effects Button**
Turns off all video effects in this section with one click.

---

### **Colour Options**

#### **Sepia / B&W**

Checkbox to enable color grading.

Two mode options:
- **Sepia** — Warm, vintage brown tone
- **Black & White** — Desaturated grayscale

**Example:** Sepia for a retro film intro; B&W for a classic documentary intro.

#### **Fade to Colour**

Checkbox to enable color fade.

When enabled:
- **Colour:** Color picker (presets: black, white, red, blue, green, #ff8800, #220022)
- **Duration (s):** Fade duration (0.3–5.0 seconds, default 1.5)

The video fades TO the chosen color at the start and FROM that color at the end.

**Example:** Fade to black for 1.5s at start, then fade from black at the end. Classic theatrical fade.

#### **Colour Grading**

Checkbox: **"Colour Grading"** — Enables contrast/brightness/saturation adjustments.

- **Contrast:** 1.12x (boosted)
- **Brightness:** +0.02 (slightly brighter)
- **Saturation:** 1.25x (more vivid colors)

These are fixed presets; no sliders. Gives a polished, TV-ready look.

**Use case:** When your background video looks flat or desaturated.

#### **Colour Shift**

Checkbox: **"Colour Shift"** — Slow hue rotation over the duration.

The entire color palette rotates through the color wheel gradually, giving a psychedelic or retro computer effect.

**Use case:** Abstract, artistic, hypnotic intros.

---

## **Section 4: Audio**

### **Fade In / Out**

Checkbox (default: enabled) — Crossfade at audio start and end.

**Fade duration (s):** 0.1–4.0 seconds (default 1.5)

Prevents jarring audio clicks or pops.

**Example:** 1.5-second fade-in + 1.5-second fade-out on a 10-second intro.

### **Master Volume**

Slider: 0.0–4.0x (default 1.0x)

Scales the overall audio level.

- **0.5x** — Half volume
- **1.0x** — Original level (default)
- **2.0x** — Double volume

**Example:** Your voiceover is quiet; boost to 1.5x. Background music is too loud; reduce to 0.7x.

### **Audio Effects**

Two columns of toggles for audio processing:

#### **Left Column (5 effects)**

**1. Bass Punch**
- Boosts low-frequency response
- **Fine-tuning:**
  - **Bass freq (Hz):** 30–300 Hz (default 80)
  - **Bass gain (dB):** 0–18 dB (default 6)
- **Use case:** Music intros, club/EDM content

**2. Reverb**
- Hall reverb effect (sounds like a large room)
- **Fine-tuning:**
  - **Reverb delay (ms):** 10–200 ms (default 40)
  - **Reverb decay:** 0.05–1.0 (default 0.5)
- **Use case:** Spacious, cathedral-like quality

**3. Stereo Widener**
- Expands the stereo image (wider left/right separation)
- **Use case:** Makes mono audio feel fuller

**4. Compressor**
- Dynamic range control (quiets loud peaks, lifts quiet parts)
- **Fine-tuning:**
  - **Comp. threshold (dB):** −40 to 0 dB (default −18)
  - **Comp. ratio:** 1.0–20.0 (default 4.0)
- **Use case:** Stabilizes inconsistent voiceovers

**5. Echo / Delay**
- Slap-back echo effect
- **Fine-tuning:**
  - **Echo delay (ms):** 10–500 ms (default 80)
  - **Echo decay:** 0.1–0.95 (default 0.35)
- **Use case:** Psychoacoustic depth, 80s retro

#### **Right Column (5 effects)**

**1. High-Pass Filter**
- Removes frequencies below a cutoff
- **Fine-tuning:**
  - **High-pass freq (Hz):** 20–800 Hz (default 80)
- **Use case:** Remove rumble, pops, or 60Hz hum

**2. Low-Pass Filter**
- Softens/removes frequencies above a cutoff
- **Fine-tuning:**
  - **Low-pass freq (Hz):** 1000–20000 Hz (default 12000)
- **Use case:** Remove harsh sibilance or high-frequency noise

**3. Normalize**
- Automatically scales audio to −16 LUFS (industry standard loudness)
- **Use case:** Ensures consistent loudness across intros

**4. Tremolo**
- Rhythmic volume pulse (tremolo/vibrato effect)
- **Fine-tuning:**
  - **Tremolo rate (Hz):** 0.5–20 Hz (default 5)
  - **Tremolo depth:** 0–1.0 (default 0.5)
- **Use case:** Rhythmic, pulsing intros; synchronized with music

**5. Chorus**
- Rich chorus effect (shimmer/width)
- **Use case:** Vocal polish, synth richness

#### **Reset Audio Effects Button**
Turns off all audio effect toggles (but not fade/volume).

**Example Scenario:** Professional voiceover workflow
1. Enable **Fade In/Out** (1.5s each end)
2. Enable **Normalize** (fix loudness)
3. Enable **High-Pass Filter** (80 Hz cutoff to remove rumble)
4. Enable **Compressor** (−18 dB threshold, 4:1 ratio to smooth dynamics)
5. Set **Master Volume** to 1.0x

Result: Professional, clean, broadcast-ready audio.

---

## **Section 5: Quality**

Located below the other tabs on the Source & Output tab.

### **CRF (Constant Rate Factor)**

A slider controlling video compression quality.

- **Range:** Varies by codec (e.g., 12–30 for H.264)
- **Lower values** = Higher quality, larger file
- **Higher values** = Lower quality, smaller file

**Default presets by format:**
- **H.264** (mp4_h264_aac): 18 (visually lossless)
- **H.265** (mp4_h265_aac, mkv_h265_aac): 22 (visually lossless)
- **VP9** (webm_vp9_opus): 24 (high quality)
- **ProRes** (mov_prores): N/A (lossless)
- **GIF**: N/A (palette-based)

**Quick guideline:**
- CRF 16–18: Maximum quality (large file)
- CRF 20–23: High quality (balanced)
- CRF 25–28: Good quality (smaller file)
- CRF 30+: Noticeably lossy (tiny file)

**Example:** For Plex playback on local network, CRF 20 is excellent. For internet streaming, CRF 24 saves bandwidth.

### **Preset**

A dropdown: `ultrafast`, `veryfast`, `fast`, `medium`, `slow`, `veryslow`

Controls encoding speed vs. compression efficiency (CPU time vs. file size).

- **ultrafast** — Fastest encoding, larger file, uses less RAM (Pi-friendly)
- **medium** — Balanced
- **veryslow** — Slowest encoding, best compression, high RAM (overkill for intros)

**Recommendation:** On Raspberry Pi or low-power systems, use `ultrafast`. On modern PCs, `fast` or `medium` is fine.

---

## **Build Log & Status Panel**

### **Build Log**

A scrolling text display (green on black terminal-style) showing all ffmpeg operations in real-time.

**Buttons:**
- **Clear Log** — Erase all log text
- **Copy Log** — Copy entire log to clipboard (useful for debugging)

**Example output:**
```
==================================================
***  INTRO BUILDER  v1.0  ***
==================================================
  BG      : /home/user/background.mp4
  Audio   : provided  /  /home/user/voiceover.wav
  Dur     : 8s  seek=0s

>> [1/3] Background...
  vf_bg   : fps=30,scale=1920:1080,format=yuv420p
  $ ffmpeg -y -threads 2 -i /home/user/background.mp4 ...
  frame= 240 fps=120 q=-1 Lsize=N/A time=00:00:08.00 ...

>> [2/3] Audio...
>> [3/3] Compositing...
  [OK] Done in 12.3s
       File size : 8.45 MB
       Output    : /home/user/intro_output.mp4
```

### **Progress Bar**

Visual progress indicator (0–100%) spanning the three build phases.

### **Status Label**

Short text status: "Ready", "1/3 Background...", "[OK] Done in 12.3s", etc.

---

## **Bottom Control Bar**

### **[>] BUILD INTRO**

Large green button. Click to start building. Disables during build, re-enables when complete.

Runs the full pipeline:
1. Transcode background to intermediate format
2. Process audio (decode, apply effects, re-encode)
3. Composite everything together with all filters/overlays

Estimated times:
- 8-second intro: 15–30 seconds (on modern hardware)
- Raspberry Pi: 2–5 minutes

### **[S] SAVE AS**

Only enabled after a successful build. Opens a file save dialog to copy the output to a new location.

**Example:** Build to `/tmp/intro_output.mp4`, then click **SAVE AS** to copy to `/home/user/videos/custom_intro.mp4`.

### **[P] PREVIEW**

Only enabled after a successful build. Opens the output file in VLC media player (if installed).

---

## **Practical Workflows & Examples**

### **Example 1: Corporate Intro with Voiceover**

1. **Source & Output tab:**
   - Select a 1080p video of your office/building (10 seconds)
   - Audio Source: "Provided track"
   - Select your recorded voiceover (.mp3 or .wav)
   - Output filename: `corporate_intro_v1`

2. **Text & Overlays tab:**
   - Overlay Text: `YOUR COMPANY NAME`
   - Font: Arial, Size: 240, Color: white, Border: 8
   - Position: Top-Center
   - Enable Text Fade: Fade in at 1s (duration 1s), fade out from 7s (duration 1s)
   - Enable Countdown Footer: Count from 5, Font size 80, white, Bottom-Centre

3. **Video & Colour tab:**
   - Enable Vignette (darkened edges for focus)
   - Enable Fade to Colour: Black, 1.5s (professional fade in/out)

4. **Audio tab:**
   - Fade In/Out: 1.5s (default)
   - Enable Normalize (for consistent loudness)
   - Master Volume: 1.0x
   - Enable Compressor (smooth any peaks in voiceover)

5. **Quality tab:**
   - Format: mp4_h264_aac
   - CRF: 20 (high quality, balanced file size)
   - Preset: fast

6. Click **[>] BUILD INTRO** → 20–30 seconds → Done!
7. Click **[P] PREVIEW** to watch in VLC
8. Click **[S] SAVE AS** to save to your final location

---

### **Example 2: Energetic Music Video Intro**

1. **Source & Output tab:**
   - Select a 4K music video or stock footage (15 seconds)
   - Audio Source: "Original background track"
   - Duration: 8s
   - BG Start: 2.0s (skip intro buildup)
   - Output filename: `music_video_intro`

2. **Text & Overlays tab:**
   - Overlay Text: `ARTIST NAME\nNEW ALBUM 2024`
   - Font: Impact, Size: 200, Color: #ff8844 (orange), Border: 6
   - Position: Center
   - Enable Text Fade: In at 0.5s (1s duration), out at 5.5s (1.5s duration)

3. **Video & Colour tab:**
   - Enable Pulse (rhythmic zoom)
   - Enable Bloom (soft glow)
   - Enable Sharpen (crisp details)
   - Enable Colour Grading (vibrant colors)
   - Enable Colour Shift (hue rotation)

4. **Audio tab:**
   - Fade In/Out: 0.5s (quick fades for music)
   - Enable Bass Punch: 80 Hz, 8 dB gain
   - Enable Stereo Widener (expansive sound)
   - Enable Normalize
   - Master Volume: 0.9x (slightly compressed to prevent clipping)

5. **Quality tab:**
   - Format: mp4_h265_aac
   - CRF: 22 (visually lossless H.265)
   - Preset: medium

---

### **Example 3: Movie Trailer with Lower Third**

1. **Source & Output tab:**
   - Select a 2K movie clip (12 seconds)
   - Audio Source: "Original background track"
   - Duration: 8s
   - Output filename: `movie_trailer_intro`

2. **Text & Overlays tab:**
   - Overlay Text: (leave blank)
   - Enable Lower Third:
     - Title: `COMING SOON`
     - Sub: `Summer 2024`
     - Display from 2.0s to 7.0s
     - Animation: Slide in/out
     - Box colour: #220011 (dark red), Opacity: 0.8
   - Enable Countdown Footer: From 5, Size 120, red, Bottom-Centre

3. **Video & Colour tab:**
   - Enable Letterbox (cinema aspect ratio)
   - Enable Fade to Colour: Black, 1.5s
   - Enable Vignette

4. **Audio tab:**
   - Fade In/Out: 2.0s (dramatic)
   - Enable Compressor (smooth dialogue)
   - Master Volume: 1.0x

5. **Quality tab:**
   - Format: mp4_h264_aac
   - CRF: 18 (maximum quality)
   - Preset: slow

---

### **Example 4: Retro Gaming Intro**

1. **Source & Output tab:**
   - Select a retro video game screenshot or recording
   - Audio Source: "Provided track"
   - Select your 8-bit/chiptune audio file (.mp3)
   - Duration: 6s
   - Output filename: `retro_gaming_intro`

2. **Text & Overlays tab:**
   - Overlay Text: `INSERT COIN\nTO CONTINUE`
   - Font: Courier New, Size: 160, Color: #88ffcc (mint green), Border: 4
   - Position: Center
   - Enable Text Fade: Constant, no fade (leave unchecked for flashing effect)

3. **Video & Colour tab:**
   - Enable Scanline Sweep (CRT scanner effect)
   - Enable Film Grain (analog feel)
   - Enable Colour Shift (retro color cycling)
   - Disable all modern effects

4. **Audio tab:**
   - Fade In/Out: 1.0s
   - Enable Echo/Delay: 80 ms delay, 0.35 decay (adds retro depth)
   - Master Volume: 1.0x

5. **Quality tab:**
   - Format: gif_animated (for classic looping GIF format)
   - CRF: N/A (not used for GIF)
   - Preset: medium

---

### **Example 5: Static Image + Narration (No Video Background)**

1. **Source & Output tab:**
   - Select a PNG company logo or promotional image
   - Audio Source: "Provided track"
   - Select your narration (.wav or .mp3)
   - Duration: 10s
   - Preserve aspect ratio: ✓ (checked)
   - Padding colour: black
   - Output filename: `logo_narration_intro`

2. **Text & Overlays tab:**
   - Overlay Text: (optional)

3. **Video & Colour tab:**
   - Enable Drift (subtle pan left to right)
   - Enable Vignette (focus on center image)

4. **Audio tab:**
   - Fade In/Out: 1.5s
   - Enable Normalize
   - Master Volume: 1.0x

5. **Quality tab:**
   - Format: mp4_h264_aac
   - CRF: 20
   - Preset: fast

---

## **Tips & Tricks**

### **Performance Tips**

- On Raspberry Pi, use **Preset: ultrafast** to save RAM
- Use **smaller source videos** (1080p instead of 4K) for faster processing
- **Disable heavy effects** like Mirror Tiles and Bloom if encoding is slow
- Use **Format: mp4_h264_aac** for fastest encoding

### **Quality Tips**

- For **local playback** (Plex), CRF 18–20 is overkill; use 22–24
- For **streaming**, use CRF 28–30 to reduce bandwidth
- Always enable **Normalize** on audio for consistent loudness
- Use **Compressor** for voiceovers to tame dynamic range

### **Creative Tips**

- **Combine effects** — Bloom + Colour Grading + Fade to Colour for a polished look
- **Text positioning** — Use **Lower Third** for news/sports, **Center** for dramatic reveals
- **Countdown** — Usually appears in last 5–10 seconds; use a bright color for visibility
- **Audio fades** — Match video fade durations for seamless transitions
- **Refresh rates** — Most intros work well at 30fps; music videos at 60fps (encoder will match)

### **Troubleshooting**

| Issue | Solution |
|-------|----------|
| **Build fails with SIGSEGV** | Reduce Duration, disable Mirror Tiles, use ultrafast preset, pre-scale video to 1080p |
| **Audio cuts off or loops incorrectly** | Check "Track End" value; 0 = loop to duration, set explicit end time if needed |
| **Text looks pixelated** | Increase Font Size; try a different font; ensure video is 1080p or higher |
| **VLC won't open** | Install with `sudo apt install vlc`; Preview still works without it |
| **Output file is huge** | Lower CRF value (increase to 24–28), change to H.265 (mkv_h265_aac) or VP9 (webm_vp9_opus) |
| **Missing fonts** | System fonts in `/usr/share/fonts` are searched; if custom font not found, Impact/Arial are fallbacks |

---

## **Keyboard Shortcuts (Tkinter Native)**

- **Tab** — Move between input fields
- **Enter** (in text box) — Add new line
- **Ctrl+C** (in log) — Copy selection (or use Copy Log button)

---

## **File Locations**

- **Application:** Same directory as `Intro_Builder.py`
- **Output videos:** Same directory as the script
- **Temporary files:** `/tmp/` (cleaned up after build)
- **Settings metadata:** Embedded in video file's comment tag (if "Embed settings" is enabled)

---

## **Saving & Loading Presets**

Click **[ LOAD SETTINGS FROM FILE ]** at the top to restore all settings from a previously built video.

**Workflow:**
1. Build an intro with all your custom settings
2. Enable "Embed settings in output file" (default)
3. Later, click **[ LOAD SETTINGS FROM FILE ]**, select the output video
4. All settings restore (text, effects, audio, timing)
5. Modify as needed, rebuild

---

## **Conclusion**

Intro Builder is a flexible, powerful tool for creating professional video intros without any command-line knowledge. The combination of video effects, text overlays, audio processing, and color grading gives you studio-quality results suitable for Plex, Jellyfin, YouTube, TikTok, and broadcast use.

Start with one of the examples above, experiment with different effect combinations, and save your work as metadata. Have fun creating! 🎬
