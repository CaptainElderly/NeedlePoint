A script designed to help artists identify the source of paywalled content leaks.

Attempts to hide a watermark inside of an image using a dithering pattern. Ideally undetectable without zooming in.
Watermark may then be extracted using another function

The main objective of this is to create watermarks which don't interfere with the enjoyment of an image, but are difficult to remove.
Can batch create unique copies for a list of usernames. 

Support small artists.

NOTE: This version is a prototype and does not contain any functionality to prevent reverse engineering. At this point i would consider it unsafe to use for art protection.


Usage


py watermark.py [image] [jpeg quality] [dither pattern]

Example of affected image:
![boowomp](https://user-images.githubusercontent.com/85809346/143182638-e32777bb-5c50-4d7b-b795-9f7afbfe44f9.jpg)
Watermark extracted using original:
![boowomp jpg_analysis](https://user-images.githubusercontent.com/85809346/143182641-c4af431a-3991-4983-b2b8-d2b4b045b7eb.png)
Close up on watermark:
![image](https://user-images.githubusercontent.com/85809346/143182696-0ce5ac58-3fac-4c94-8180-ec8390196910.png)
