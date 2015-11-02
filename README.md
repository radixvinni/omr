Optical music recognition
===

I was desperately trying to find the OMR library that works and the only thing i found was this. The quality is not the best, but better than nothing. It uses OpenCV-python - that should be installed.

Usage
===

0. If you have a pdf file convert it to image. On Unix you would use imagemagick:

		convert -density 150 -quality 90 -background white -alpha remove your.pdf source.png

1. The next thing you should do is to remove the staff lines. Run: 

		python omr_main.py source.png

	That should calculate and print a threshold for you image, create file staff_removal_source.png without horisontal staff lines and ask you to press enter to continue. If the lines were not removed in that file, you must increase a threshold and rerun a tool. Otherwise, proceed to the next step.

2. Press enter to continue recognition. OpenCV should find and recognize all the musical symbols in a file without the lines. Open the file recognition_output_source.png and check if all symbols are marked with rectangles. If not, recognition threshold must be increased.

3. Than the script performs reconstruction of the Lilypond and MusicXML files by dictionary with recognised musicalObjects (see module omr_reconstruction.py). If some of them were not recognized but must be present, that would give an Exception on this step. Otherwise it will produce files source.ly (in Lilypond format) and source.xml (in musicXML).

4. You can convert the result to midi with lilypond and play it with timidity:

		lilypond -dmidi-extension=mid source.ly
		timidity source.mid
