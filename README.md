## Dataflow

![](dataflow.png)


## Steps

1. Download
	
Download image dataset (raw, original files) into `raw` directory.

2. Preprocess

`sh preprocess`

Resize, rename, and/or convert raw images into `pre` directory. This step needs [ffmpeg](https://ffmpeg.org/ffmpeg.html) and [sips](https://ss64.com/osx/sips.html)

3. Analyze images

`sh analyze`

Output two files: an entry file and a data file

A: Entry file contains one entry per image file holding the following data: 

  -	brightness: variance of the image histogram
  -	bodies    : number of bodies found (haarcascades)
  -	faces     : number of faces found (haarcascades)
  -	cvblobs   : number of cvblobs found
  -	lines     : number of hough lines found
  -	circles   : number of hough circles found
  -	keypoints : number of keypoints (corners) found

B: `JSON` data files contains one entry per image file holding the actual data

[mean_col (x), histo (64), bodies (x), faces (x), cvblobs (x), lines (x), circles (x), keypoints (x)]

Optionally:

Define a ROI using the `roi.pd` patch, and then setting the ROI flag to 1 before running `sh analyze`

4. Sorter

`sh sorter`

Use A to sort files based on any given field, and pairs of fields

Output sorted files into `*-sorted.txt` where each line contains
the sorted inidices of each image filename.

5. Concatenate `JSON` files into one

`python src/catjson.py`

Places all data objects (B) inside an array of objects in one `JSON` object (C)


6. Reader 

`cd bin`
`pd reader.pd`

This patch can be used to:

-  visualize the `JSON` data files (B)
-  play the sorted sequences from (4)


7. Query

`cd bin`
`pd query.pd`

NOTE: This patch is a gui for `src/query.py`.

This patch can be used to:

-  perform a query to the `JSON` data base (C) to get indices, based on 
-  multiple descriptors (color, brightness, smoothness, blobiness, etc.), 
-  visualize the queries for live editing with the `sh display` program

Both input query and its results are stored on `JSON` files for later use.











