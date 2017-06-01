## Project: Search and Sample Return
### Well, lets sent a rover to Mars :)
(but not this, not mine, not yet)

---

[image1]: ./output/cordinate_transformation.png
## 1. A Writeup

This is a writeup or a procedure on how i tackled some of the problems during the first project in Udacity's Robotics Nanodegree. 

## 2. Notebook Analysis
Due to the fact that in the early stages i had problems with Jupyter Notebooks, could not import `moviepy` (and still have), i decided to work in PyCharm and then in the end, copied everything and put in Notebook again!

So, not to repeat myself from what i said in Notebook, i will explain here how i did color thresholding.

Firstly i used the method that we created in the begining of class:
```python
def color_terrain(img):
    color_select = np.zeros_like(img[:,:,0])
    above_thresh = (img[:,:,0] > 160) \
                & (img[:,:,1] > 160) \
                & (img[:,:,2] > 160)
    color_select[above_thresh] = 1
    return color_select
```

This returned an array masked with 1 or True where was navigable terrain, and 0 or false where were obsticals or rock, which brings me to the second point, logically, to determine the non-navigable terrain, we just use the inverse of this functio. I simply changed the sign from > to <:  
```python
def color_terrain(img):
    color_select = np.zeros_like(img[:,:,0])
    above_thresh = (img[:,:,0] < 160) \
                & (img[:,:,1] < 160) \
                & (img[:,:,2] < 160)
    color_select[above_thresh] = 1
    return color_select
```
And lastly, but very importantly, detecting rocks.
Well, this was abt more trickier, as i had to manipulate with upper and lower boundaries, i went using openCV, and we already used it for some image warping (so no need for extra-import). I did masking based on threshold placed below (based on HSV, as the image is converted to HSV).
```python
def color_rocks(img):
    lower_thresh = np.array([20, 100, 100])
    upper_thresh = np.array([25, 255, 255])
    color_select = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_RGB2HSV, 3), lower_thresh, upper_thresh)
    return color_select
```

Later on, during the process i changed the color_rocks() from using OpenCV to again using NumPy:

```python
def color_rocks(img):
    color_select = np.zeros_like(img[:, :, 0])
    thresh = (img[:, :, 0] > 100) & (img[:, :, 0] < 255) \
             & (img[:, :, 1] > 100) & (img[:, :, 1] < 255) \
             & (img[:, :, 2] > 0) & (img[:, :, 2] < 75)
    color_select[thresh] = 1
    return color_select
```

This seemed to be working better in the decision step to get the angle and pixel size so that the rover can move better!

After mapping the terrain, warping and matrix transformation and rotation, i got this:


![alt text][image1]

From here i used the Databucket() class, to make pandas dataframe and go through all pictures that i recorded during first run.
**The video of output is in `./output` folder**

### Populating process_image() function in the notebook was straight forward, all the methods were already touched during the class and in notebook!



#### But each step was as follows:

1. Based on pixels of grid picture that was given, we marked the exact pixels for source and destination

2. I used openCV warp function to make an image from camera-point-of-view to bird-eye-point-of-veie

3. Color thresholding of terrain, obsicles and rocks

4. Mapping to real world coordinates

5. **Then finding the angle where most of navigable terrain was (so we steer that way) and the distance**

   ```python
   xpix, ypix = rover_coords(threshed)
   dist, angles = to_polar_coords(xpix, ypix)
   mean_dir = np.mean(angles)
   ```

6. Plotting the results in the window




## 3. Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` and `decision_step()`  functions in the autonomous mapping scripts.




#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

