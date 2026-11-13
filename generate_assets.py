import os
from PIL import Image

src = 'E:/Job Hunt/job-hunter-repo/logo.png'
im = Image.open(src).convert('RGBA')

inst_dir = 'E:/Job Hunt/job-hunter-repo/installer'
app_dir = r'C:\Users\USER\AppData\Local\Programs\Pasha Hunt'

for size, name in [(150, 'Square150x150Logo.png'), (70, 'Square70x70Logo.png'), (44, 'Square44x44Logo.png')]:
    resized = im.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(os.path.join(inst_dir, name))
    if os.path.exists(app_dir):
        resized.save(os.path.join(app_dir, name))

manifest_content = """<Application xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <VisualElements
      ShowNameOnSquare150x150Logo="on"
      Square150x150Logo="Square150x150Logo.png"
      Square70x70Logo="Square70x70Logo.png"
      ForegroundText="light"
      BackgroundColor="#0f172a"/>
</Application>"""

with open('E:/Job Hunt/job-hunter-repo/installer/PashaHunt.VisualElementsManifest.xml', 'w') as f:
    f.write(manifest_content)

with open('E:/Job Hunt/job-hunter-repo/PashaHunt.VisualElementsManifest.xml', 'w') as f:
    f.write(manifest_content)

if os.path.exists(app_dir):
    with open(os.path.join(app_dir, 'PashaHunt.VisualElementsManifest.xml'), 'w') as f:
        f.write(manifest_content)

print('VisualElementsManifest and assets successfully created!')

