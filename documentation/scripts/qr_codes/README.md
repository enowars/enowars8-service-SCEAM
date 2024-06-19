- pillow is slow, whatever you do do not use it
- small mask application is only supported in pillow

- cv2 is slow at loading images, but fast at resizing
- numpy is slower at handling images than pure cv2

- reading images straight from the segno buffer is super slow with resizing and upscaling
- it is quicker to save segno to buffer, open with pillow, convert to rgm and make numpy array
- than to save directly to numpy array from internal matrix buffer
- i have no clue why the above is true but it is

- current best is:
  - to preload background as numpy array
  - generate segno with 0 border and desired scale
  - save to buffer
  - open with pillow
  - convert to rgb
  - convert to numpy array
  - cv2copyMakeBorder to desired size
  - numpy magic to overlap on pregenerated mask
