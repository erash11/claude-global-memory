on run argv
	set inPath to item 1 of argv
	set outPath to item 2 of argv
	tell application "Microsoft Word"
		set theDoc to open file name inPath with read only
		save as theDoc file name outPath file format format PDF
		close theDoc saving no
	end tell
	return "ok"
end run
