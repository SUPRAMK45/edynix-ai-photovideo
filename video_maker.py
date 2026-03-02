from flask import Flask, render_template, request, send_file
from moviepy import ImageClip, concatenate_videoclips, ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return render_template('photo_home.html')


@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist("photos")
    duration = int(request.form.get("duration", 3))  # default 3 sec

    if not files:
        return "No files uploaded"

    image_paths = []

    for file in files:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        image_paths.append(filepath)

    clips = []

    TARGET_WIDTH = 1280
    TARGET_HEIGHT = 720

    for img in image_paths:
        clip = ImageClip(img)
        clip = clip.resized(height=TARGET_HEIGHT)

        background = ColorClip(
            size=(TARGET_WIDTH, TARGET_HEIGHT),
            color=(0, 0, 0)
        ).with_duration(duration)

        clip = clip.with_position("center").with_duration(duration)

        final_clip = CompositeVideoClip([background, clip])
        clips.append(final_clip)

    final_video = concatenate_videoclips(clips)

    output_path = os.path.join(OUTPUT_FOLDER, "final_video.mp4")

    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264"
    )

    return send_file(output_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)