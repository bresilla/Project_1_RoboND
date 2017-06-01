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

Here gos the most important part of the project!

#### `perception_step()`

I immediately started populating the perception_step() with the calls for the methods that we made during the class.

Firstly i  created some variables.

```python
cam_offset = 6 #rover camera offset caibration parameter
dst_size = 5
world_scale = 30
world_size = Rover.worldmap.shape[0]
```

Then based on the grid image, we (during the class) marked the points where are the four corners for 1 square meter from the source picture, and what will be the destination of those four points after warping and looking from different perspective.

```python
source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
destination = np.float32([[Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - bottom_offset],
                      [Rover.img.shape[1]/2 + dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                      [Rover.img.shape[1]/2 - dst_size, Rover.img.shape[0] - 2*dst_size - bottom_offset],
                      ])
```
Then warping the image. This uses a function from `openCV` to warp and transform the image. From openCV documentation:

 *For perspective transformation, you need a 3x3 transformation matrix. Straight lines will remain straight even after the transformation. To  find this transformation matrix, you need 4 points on the input image  and corresponding points on the output image. Among these 4 points, 3 of  them should not be collinear. Then transformation matrix can be found by the function **cv2.getPerspectiveTransform**. Then apply **cv2.warpPerspective** with this 3x3 transformation matrix.*

```python
warped = perspect_transform(Rover.img, source, destination)
```

 Then we identify terrain, rocks and obstacles as described above, and here we just call those functions:

```python
terrain_select = color_terrain(warped)
obstcls_select = color_obstcls(warped)
rocks_select = color_rocks(warped)
```

After successful identification and thresholding, we use `Rover.vision_image` to draw those elements in the map for the simulator: (it was challenging, as the map would not show the images unless multiplying at the end with 255 <- i guess the color channel and depth) (thanks to @tiedyedguy for helping me out)

```python
Rover.vision_image[:, :, 2] = terrain_select * 255
Rover.vision_image[:, :, 0] = obstcls_select * 255
Rover.vision_image[:, :, 1] = rocks_select * 255
```

After that, was mapping the view to real world view:

```python
terrain_xpix, terrain_ypix = rover_coords(terrain_select)
obstcls_xpix, oobstcls_ypix = rover_coords(obstcls_select)
rocks_xpix, rocks_ypix = rover_coords(rocks_select)

pos = Rover.pos
yaw = Rover.yaw
terrain_x_world, terrain_y_world = pix_to_world(terrain_xpix, terrain_ypix, pos[0], pos[1], yaw, world_size, world_scale)
obstcls_x_world, obstcls_y_world = pix_to_world(obstcls_xpix, oobstcls_ypix, pos[0], pos[1], yaw, world_size, world_scale)
rocks_x_world, rocks_y_world = pix_to_world(rocks_xpix, rocks_ypix, pos[0], pos[1], yaw, world_size, world_scale)
```

Here, thanks to the hint of @shreeyak i made a conditional step to improve the fidelity, and not letting the pitch or roll have high values as they would highly impact the fidelity.

```python
if Rover.roll < 2.0 or Rover.roll > 358:
    if Rover.pitch < 2.0 or Rover.pitch > 358:
        Rover.worldmap[obstcls_y_world, obstcls_x_world, 0] += 255
        Rover.worldmap[rocks_y_world, rocks_x_world , 1] += 255
        Rover.worldmap[terrain_y_world, terrain_x_world, 2] += 255
```

Lastly, getting the angle and pixels position so the rover knows where is the navigable terrain, and calculating mean angle for steering. In addition to terrain, there is also rocks (and less important obstacles).

Then everything is assign to Rover calss and returned the Rover.

```python
terrain_dist, terrain_angles = to_polar_coords(terrain_xpix, terrain_ypix)
rock_dist, rock_angles = to_polar_coords(rocks_xpix, rocks_ypix)
obstcls_dist, obstcls_angles = to_polar_coords(obstcls_xpix, oobstcls_ypix)

Rover.nav_dists, Rover.nav_angles = terrain_dist, terrain_angles
Rover.rocks_dists, Rover.rocks_angles = rock_dist, rock_angles
Rover.obstcls_dists, Rover.obstcls_angles = obstcls_dist, obstcls_angles
```

#### `class RoverState():`

I added few lines of code in `drive_rover.py` to accommodate those, as those are very important in steering the rover in the direction of the rock, when rover sees it based on color_threshold of it:

```python
        self.rocks_dists = None
        self.rocks_angles = None
        self.obstcls_dists = None
        self.obstcls_angles = None
```

#### `decision_step()`

Here is the basic logic served to us:

```python
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward *2:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'

    # Just to make the rover do something
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
```

 And, actually for basic navigation it works just fine. Without modification, the rover goes through the map, follows the most navigable terrain, sometime spins a lot, but it works.

My first added code in this logic was two lines, that simply stop the rover near the sample, as sometime it goes through  it and since there is velocity, it does not stop. 

```python
    if Rover.near_sample:
        Rover.brake = Rover.brake_set
```

Is simple, hitting the breaks when near sample, and when near sample, it automatically picks up the sample:

```python
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
```

Then the next chunk of code was added to follow the rock when it sees it:

```python
    if Rover.rocks_angles is not None and len(Rover.rocks_angles) > 0:
        Rover.steer = np.clip(np.mean(Rover.rocks_angles * 180/np.pi), -15, 15)
        if not Rover.near_sample:
            if Rover.vel < 1:
                Rover.brake = 0
                Rover.throttle = 0.1
        else:
            Rover.throttle = 0
            Rover.brake = Rover.brake_set
```



#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

So, launching in autonomous mode, it actually works pretty well. it navigates the terrain with quiet high fidelity! It still spins sometime and is not able to avoid small obstacles.

How i can improve that:

Firstly, i think that when thresholding and then creating the navigable terrain, i can restrict the distance of this terrain, so i don't consider terrain further away than 2 or three meters from robot, and in this was i can make a mean angle that is more robust on just those near pixels.

Secondly, decision step. There are many many ways that this changes the behaviour of the robot. Adding a time function, as when it spins for more than `x` amount of time/frames then, change the angle. Then when stuck for too much time, got to stop more and spin in the other side, and so on...

I think the decision step is very entertaining, as it makes use of logic and taking actions based on the input you get. 



## So, this mark the end of my project! I was soo blown away that in just week one we covered all those basics concept. And to think of, its a lot, but was so attractive (sorry for lack of my english vocabulary), so i could not even go and do something else. Cant wait for next project!