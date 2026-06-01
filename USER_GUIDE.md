# Intro Builder v1.0 — Complete User Guide

## Overview

**Intro Builder** is a Python-based GUI application that creates custom pre-roll intro videos for media servers like **Plex**, **Jellyfin**, and other video platforms. It combines background video/images, audio, text overlays, and advanced video/audio effects into professional-looking intros with full customization.

---

## Table of Contents

1. [Installation](#installation)
2. [System Requirements](#system-requirements)
3. [First Launch](#first-launch)
4. [User Interface Guide](#user-interface-guide)
5. [Example Use Cases](#example-use-cases)
6. [Settings & Presets](#settings--presets)
7. [Troubleshooting](#troubleshooting)
8. [Tips & Tricks](#tips--tricks)

---

## Installation

### Prerequisites

Before running Intro Builder, ensure you have:

1. **Python 3.7+** installed
2. **FFmpeg** (with ffprobe) — latest version
3. **VLC** (for preview functionality)

### Step-by-Step Installation

#### **Linux (Debian/Ubuntu/Raspberry Pi)**

```bash
# Update package manager
sudo apt update

# Install Python3, FFmpeg, and VLC
sudo apt install python3 python3-tk ffmpeg vlc

# Verify installations
python3 --version
ffmpeg -version
vlc --version
```

#### **macOS**

```bash
# Using Homebrew (install Homebrew first if needed)
brew install python3 ffmpeg vlc
```

#### **Windows**

1. Install **Python 3** from [python.org](https://www.python.org/downloads/) (ensure "Add to PATH" is checked)
2. Install **FFmpeg**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH, or use Chocolatey:
   ```powershell
   choco install ffmpeg vlc
   ```
3. Install **VLC**: Download from [videolan.org](https://www.videolan.org/vlc/)

### Running Intro Builder

#### **Linux/macOS**

```bash
# Make the script executable
chmod +x "Intro _Builder.py"

# Run it
./Intro\ _Builder.py

# OR use Python directly
python3 Intro\ _Builder.py
```

#### **Windows**

```bash
python "Intro _Builder.py"
```

---

## System Requirements

| Component         | Minimum                 | Recommended      |
|-------------------|------------------------|------------------|
| **CPU**           | 2-core @ 1.5GHz        | 4-core @ 2.0GHz+ |
| **RAM**           | 2 GB                   | 4 GB+            |
| **Storage**       | 1 GB free              | 5 GB+            |
| **Python**        | 3.7+                   | 3.10+            |
| **FFmpeg**        | Latest stable          | Latest stable    |
| **Display**       | 1280×800 minimum       | 1920×1080+       |

**Note**: Tested on Raspberry Pi 5 (8GB) and Manjaro Linux. Performance varies by hardware; lower-end systems may take longer to render.

---

## First Launch

1. **Execute the script** using one of the methods above
2. A dark-themed GUI window will open (titled "Intro Builder v1.0")
3. You'll see **4 tabs**: Source & Output, Text & Overlays, Video & Colour, Audio
4. A **Build Log** panel appears at the bottom
5. The **BUILD INTRO** button is in the bottom-left corner

---

## User Interface Guide

### Tab 1: Source & Output

#### **Source Files**

- **Background**: Select a video, image, or animated GIF
  - Supported formats: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.jpg`, `.png`, `.gif`
  - **Preserve aspect ratio**: Check if your image isn't 16:9 (adds padding)
  - **Padding colour**: Choose the fill color when preserving aspect ratio

#### **Audio Source**

Choose one of three options:

1. **Original background track** — Uses audio from your background video (if available)
2. **Provided track** — Specify a separate audio file (`.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`)
   - Shows duration sliders to trim or loop the audio
3. **Silent (no audio)** — No audio in the final intro

#### **Duration & Output**

- **Duration (s)**: Total length of the intro (3–300 seconds; auto-detected from background)
- **BG Start (s)**: Where to start the background video/image (seek position)
- **BG End (s)**: Where to end the background (0 = full duration)
- **Output Filename**: Name of the final video (without extension)
- **Output Format**: Choose the output codec/container
  - `mp4_h264_aac` — Most compatible (Default)
  - `mp4_h265_aac` — Smaller file size, modern
  - `webm_vp9_opus` — Open format
  - `mov_prores` — Professional editing
  - `mkv_h265_aac` — Archival
  - `gif_animated` — Animated GIF output

#### **Metadata**

- **Embed settings in output file**: When enabled, all current settings are stored as metadata in the video file. Later, use **[ LOAD SETTINGS FROM FILE ]** to restore them instantly.

---

### Tab 2: Text & Overlays

#### **Overlay Text**

- Enter text for your intro (supports multi-line: press Enter for new lines)
- **Font**: Choose from installed system fonts
- **Size**: Font size in pixels (10–500; default 180)
- **Colour**: Select text color with a color picker or preset
- **Border**: Text outline thickness (0–30 pixels)
- **Position**:
  - **Center** — Middle of the screen
  - **Top-Center** — Upper third
  - **Bottom-Center** — Lower third (above footer)
  - **Lower-Third** — Professional broadcast position

- **Opacity**: Text transparency (0–100%)
- **Text Fade**: Optional fade-in and fade-out effects
  - **Fade in after (s)**: When to start the fade-in
  - **Fade in for (s)**: Duration of fade-in
  - **Fade out from (s)**: When to start the fade-out
  - **Fade out for (s)**: Duration of fade-out

#### **Lower Third**

- **Enable**: Checkbox to activate the lower-third bar
- **Title**: Main text for the bar
- **Subtitle**: Secondary text
- **Display from/to (s)**: When the bar appears and disappears
- **Animation**: Slide in/out or fade in/out
- **Box colour**: Background color of the bar
- **Box opacity**: Transparency (0.0–1.0)

#### **Countdown Footer**

- **Enable**: Activate a countdown timer at the end of the video
- **Count from**: Starting number (2–30)
- **Font size**: Size of countdown numbers
- **Colour**: Countdown text color
- **Position**: Where the countdown appears

#### **Overlay Extras Opacity**

- Master opacity for all overlay elements (lower-third, countdown, etc.)

---

### Tab 3: Video & Colour

#### **Video Effects**

Enable/disable individual effects:

| Effect            | Description                                   |
|-------------------|-----------------------------------------------|
| **Scanline Sweep** | Animated light bar scanning across the frame |
| **Slow Drift**     | Gentle pan from left to right                 |
| **Mirror Tiles**   | 2×2 kaleidoscope effect                       |
| **Film Grain**     | Analogue noise overlay for vintage feel      |
| **Letterbox**      | Cinematic 2.35:1 black bars                   |
| **Vignette**       | Darkened edges for cinema look                |
| **Flash Bar**      | Mid-video white flash effect                  |
| **Pulse**          | Rhythmic zoom/breathe effect                  |
| **Glitch**         | Digital corruption flickers                   |
| **Bloom**          | Soft glow on highlights                       |
| **Sharpen**        | Crisp edge detail enhancement                 |

**Reset Video Effects**: Disables all video effects

#### **Colour Options**

- **Sepia / B&W**: Apply sepia tone or black & white
- **Fade to Colour**: Fade from/to a solid color at start/end
  - **Duration (s)**: How long the fade takes (0.3–5.0 seconds)
- **Colour Grading**: Adjust contrast, brightness, and saturation
- **Colour Shift**: Slow hue rotation throughout the video

---

### Tab 4: Audio

#### **Audio Effects**

**Master Volume**: Overall audio level (0.0–4.0×)

**Fade In / Out**: Crossfade at start and end of audio (enabled by default)
- **Fade duration (s)**: Length of fade (0.1–4.0 seconds)

**Left Column**:
- Bass Punch — EQ boost for low frequencies
- Reverb — Hall reverb effect (aecho)
- Stereo Widener — Wider soundstage
- Compressor — Dynamic range control
- Echo / Delay — Slap-back echo

**Right Column**:
- High-Pass Filter — Remove rumble below a cutoff frequency
- Low-Pass Filter — Soften highs above a cutoff frequency
- Normalize — Auto loudness adjustment to -16 LUFS
- Tremolo — Rhythmic volume pulse
- Chorus — Rich chorus shimmer

#### **Audio Fine-Tuning Sliders**

Detailed controls for selected effects:
- **Bass freq (Hz)**, **Bass gain (dB)**
- **Reverb delay (ms)**, **Reverb decay**
- **Compressor threshold (dB)**, **Compressor ratio**
- **High-pass/Low-pass frequencies (Hz)**
- **Echo delay (ms)**, **Echo decay**
- **Tremolo rate (Hz)**, **Tremolo depth**

**Reset Audio Effects**: Disables all audio effects and resets sliders to defaults

---

### Build & Output

#### **Quality Settings** (Tab 1, below Duration & Output)

- **CRF (Constant Rate Factor)**:
  - Lower = higher quality (larger file)
  - Different ranges for different codecs (H.264: 0–51, VP9: 0–63)
  - Default: 18 (visually lossless)

- **Preset**:
  - `ultrafast`, `veryfast`, `fast`, `medium`, `slow`, `veryslow`
  - Faster = less time, lower quality; slower = more time, best quality
  - Default: `ultrafast` (good balance)

#### **Build Button**

Click **[>] BUILD INTRO** to start rendering. The app will:

1. Process the background
2. Process the audio
3. Composite text, overlays, and effects
4. Generate the final video

Progress updates in the Build Log (bottom panel).

#### **Output Actions** (After Build)

- **[S] SAVE AS**: Save the video to a custom location
- **[P] PREVIEW**: Open in VLC to watch immediately

---

## Example Use Cases

### Example 1: Simple Studio Intro (Plex)

**Goal**: 5-second intro with your studio logo and theme music

**Steps**:

1. **Tab 1 — Source & Output**:
   - Background: Select a 1920×1080 MP4 (your studio footage)
   - Audio Source: Provided track → Select your theme `.mp3`
   - Duration: 5 seconds
   - Output Filename: `studio_intro`

2. **Tab 2 — Text & Overlays**:
   - Overlay Text: "WELCOME TO MY STUDIO"
   - Font: Impact, Size: 120
   - Colour: White
   - Position: Center
   - Enable Text Fade: Fade in at 0.5s for 0.5s, fade out from 4.0s for 0.5s

3. **Tab 3 — Video & Colour**:
   - Enable: Vignette (for cinema look)
   - Fade to Colour: Enable, Color: Black, Duration: 1.5s

4. **Tab 4 — Audio**:
   - Fade In/Out: Enabled, Duration: 1.0s
   - Master Volume: 1.0x

5. Click **BUILD INTRO**

---

### Example 2: Animated Lower-Third (Jellyfin)

**Goal**: Movie intro with lower-third "Now Playing" bar

**Steps**:

1. **Tab 1 — Source & Output**:
   - Background: A 1080p action movie clip
   - Audio Source: Original background track
   - Duration: 8 seconds
   - Output Filename: `movie_intro`

2. **Tab 2 — Text & Overlays**:
   - Overlay Text: (leave blank or minimal)
   - Lower Third — Enable:
     - Title: "NOW PLAYING"
     - Subtitle: "Action Adventure"
     - Display from: 1.0s, Display to: 7.0s
     - Animation: Slide in / slide out
     - Box colour: `#222222`, Opacity: 0.8

3. **Tab 3 — Video & Colour**:
   - Enable: Slow Drift, Pulse, Sharpen
   - Fade to Colour: Black, Duration: 1.5s

4. **Tab 4 — Audio**:
   - Bass Punch: Enabled, Boost low frequencies
   - Tremolo: Enabled (rhythmic effect)

5. Click **BUILD INTRO**

---

### Example 3: Retro VHS Intro

**Goal**: Nostalgic 8-bit style intro with glitch effects

**Steps**:

1. **Tab 1 — Source & Output**:
   - Background: An old/grainy video or image
   - Audio Source: Silent or retro chiptune music
   - Duration: 10 seconds
   - Output Filename: `retro_intro`

2. **Tab 2 — Text & Overlays**:
   - Overlay Text: "RETRO PRESENTS"
   - Font: Courier (monospace)
   - Position: Center
   - Border: 8 pixels (thick outline)

3. **Tab 3 — Video & Colour**:
   - Enable: Film Grain, Glitch, Letterbox
   - Sepia / B&W: Black & White
   - Fade to Colour: Color Shift enabled (slow hue rotation)

4. **Tab 4 — Audio**:
   - Normalize: Enabled

5. Click **BUILD INTRO**

---

### Example 4: Corporate Branding Intro

**Goal**: Professional fade-in with logo and company name

**Steps**:

1. **Tab 1 — Source & Output**:
   - Background: Company logo PNG (preserve aspect ratio)
   - Audio Source: Corporate theme music
   - Duration: 6 seconds
   - Output Filename: `company_intro`

2. **Tab 2 — Text & Overlays**:
   - Overlay Text: "ACME CORPORATION"
   - Font: Arial, Size: 200
   - Colour: Company color (e.g., `#FF6600`)
   - Position: Bottom-Center
   - Text Fade: Fade in from 0s for 2s, fade out from 4s for 2s

3. **Tab 3 — Video & Colour**:
   - Fade to Colour: Enabled, Color: White, Duration: 0.5s
   - Bloom: Enabled (soft professional glow)

4. **Tab 4 — Audio**:
   - Fade In/Out: 1.0s
   - Master Volume: 1.2x

5. Click **BUILD INTRO**

---

## Settings & Presets

### Saving & Loading Settings

The metadata feature allows you to save all settings inside the video file:

**To Save Settings**:
1. Configure everything as desired
2. Enable "Embed settings in output file" (Tab 1)
3. Click BUILD INTRO
4. Your settings are now embedded in the video

**To Load Settings**:
1. Click **[ LOAD SETTINGS FROM FILE ]** (top-right)
2. Select a previously built intro video
3. All settings are restored instantly
4. Modify as needed and rebuild

This is perfect for creating variations of intros without reconfiguring everything.

---

## Troubleshooting

### Common Issues

#### **"ffmpeg not found"**

**Solution**: Ensure FFmpeg is installed and in your system PATH.

```bash
# Test if ffmpeg is accessible
ffmpeg -version

# If not found, install it (see Installation section)
```

#### **"Out of memory" error (especially on Raspberry Pi)**

**Solution**: Reduce complexity:
- Lower **Duration** (fewer frames to process)
- Use **Preset: ultrafast** (less RAM)
- Reduce **CRF** (faster encoding)
- Disable heavy effects (Bloom, Mirror)
- Pre-scale your background to 1080p

#### **Video plays but no audio**

**Solution**:
1. Ensure Audio Source is set correctly (not "Silent")
2. Verify the audio file format is supported (`.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`)
3. Check Master Volume isn't set to 0

#### **Text appears garbled or missing**

**Solution**:
1. The font may not be installed; select a different system font
2. Use apostrophes/colons carefully (they're auto-escaped)
3. Reduce font size if text overflows the frame

#### **Build takes very long**

**Solution**:
- Use **Preset: ultrafast** or **veryfast**
- Reduce **Duration**
- Disable unused effects
- Lower **resolution** of background (pre-scale to 1080p)

#### **VLC won't open for preview**

**Solution**:
1. Ensure VLC is installed:
   ```bash
   vlc --version
   ```
2. If not found, install it (see Installation)
3. Try opening the video file manually

### Getting Help

1. **Check the Build Log**: Scroll through and look for error messages (in red)
2. **Verify Prerequisites**: Ensure Python, FFmpeg, and VLC are all installed
3. **Test with Simple Settings**: Start with minimal effects and add gradually

---

## Tips & Tricks

### Performance Tips

- **Faster Builds**: Use `ultrafast` preset + lower CRF (e.g., 20 instead of 18)
- **Smaller Files**: Use H.265 codec (`mp4_h265_aac`) — ~30% smaller than H.264
- **Preview First**: Enable effects one at a time to see which impact speed

### Quality Tips

- **Best H.264**: CRF 16–18, Preset `slow`
- **Best H.265**: CRF 20–22, Preset `slow`
- **For Archive**: Use `mov_prores` codec (larger, better for editing)

### Creative Tips

- **Multi-line Text**: Press Enter in the text field to add line breaks
- **Countdown Effect**: Use "Countdown Footer" for action sequences (e.g., "5…4…3…2…1…GO!")
- **Lower-Third Animation**: Use "Slide" for dynamic sports intros, "Fade" for professional news-style
- **Audio Layering**: Combine Bass Punch + Reverb for cinematic sound
- **Colour Grading**: Increase saturation (+25%) for vibrant intros, decrease for moody/cinematic

### Batch Processing

For multiple intros:
1. Build the first intro with settings embedded
2. Load settings from that file
3. Change only the text/position/audio
4. Rebuild (much faster than reconfiguring)

---

## Appendix: Supported File Formats

| Type       | Formats                                       |
|------------|-----------------------------------------------|
| **Video**  | `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`      |
| **Image**  | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`      |
| **Audio**  | `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`      |
| **Output** | `.mp4`, `.webm`, `.mov`, `.mkv`, `.gif`      |

---

## Glossary

- **CRF**: Constant Rate Factor — controls quality/file size (lower = better quality)
- **Preset**: Encoding speed/quality trade-off (ultrafast = fastest, veryslow = best quality)
- **Filter Chain**: Series of video/audio effects applied in sequence
- **Aspect Ratio**: Width-to-height proportion (e.g., 16:9 is standard widescreen)
- **Lower-Third**: Broadcast-style text bar in the lower portion of the screen
- **Vignette**: Darkened edges effect used in professional video
- **Bloom**: Soft glow/blurring effect on bright areas

---

## License & Credits

**Intro Builder v1.0**  
Created with assistance from Claude (Anthropic)  
Uses FFmpeg (licensed under LGPL/GPL)  
Uses VLC for preview (licensed under GPL)

---

**Happy intro building! 🎬**
