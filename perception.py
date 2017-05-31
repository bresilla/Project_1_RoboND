import cv2
import numpy as np
#<editor-fold desc="Source-Destin">
def sour():
    return np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
def dest(img, dst_size, bottom_offset):
    return np.float32([[img.shape[1] / 2 - dst_size, img.shape[0] - bottom_offset],
                              [img.shape[1] / 2 + dst_size, img.shape[0] - bottom_offset],
                              [img.shape[1] / 2 + dst_size, img.shape[0] - 2 * dst_size - bottom_offset],
                              [img.shape[1] / 2 - dst_size, img.shape[0] - 2 * dst_size - bottom_offset],])
# </editor-fold>
#<editor-fold desc="Perspective Transform">
def perspect_transform(img, src, dst):
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))
    return warped
# </editor-fold>
#<editor-fold desc="Color Thresholding">
def color_terrain(img):
    color_select = np.zeros_like(img[:,:,0])
    above_thresh = (img[:,:,0] > 160) \
                & (img[:,:,1] > 160) \
                & (img[:,:,2] > 160)
    color_select[above_thresh] = 1
    return color_select
def color_obstcls(img):
    color_select = np.zeros_like(img[:,:,0])
    above_thresh = (img[:,:,0] < 160) \
                & (img[:,:,1] < 160) \
                & (img[:,:,2] < 160)
    color_select[above_thresh] = 1
    return color_select
def color_rocks(img):
    lower_thresh = np.array([20, 100, 100])
    upper_thresh = np.array([25, 255, 255])
    color_select = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_RGB2HSV, 3), lower_thresh, upper_thresh)
    return color_select
# </editor-fold>
#<editor-fold desc="Rover radial cords">
def rover_coords(binary_img):
    ypos, xpos = binary_img.nonzero()
    x_pixel = np.absolute(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[0]).astype(np.float)
    return x_pixel, y_pixel
# </editor-fold>
#<editor-fold desc="Radial to polar cords">
def to_polar_coords(x_pixel, y_pixel):
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles
# </editor-fold>
#<editor-fold desc="Rotation matrix">
def rotate_pix(xpix, ypix, yaw):
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    return xpix_rotated, ypix_rotated
# </editor-fold>
#<editor-fold desc="Translation matrix">
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale):
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    return xpix_translated, ypix_translated
# </editor-fold>
#<editor-fold desc="Rover-centric to real-world">
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    return x_pix_world, y_pix_world
# </editor-fold>


def perception_step(Rover):
    cam_offset = 6
    world_scale = 5
    world_size = Rover.worldmap.shape[0]
    #1
    source = sour()
    destination = dest(Rover.img, world_scale, cam_offset)
    #2
    warped = perspect_transform(Rover.img, source, destination)
    #3
    terrain_select = color_terrain(warped)
    obstcls_select = color_obstcls(warped)
    rocks_select = color_rocks(warped)
    #4
    Rover.vision_image[:, :, 0] = obstcls_select * 255
    Rover.vision_image[:, :, 1] = rocks_select
    Rover.vision_image[:, :, 2] = terrain_select * 255
    #5
    terrain_xpix, terrain_ypix = rover_coords(terrain_select)
    obstcls_xpix, oobstcls_ypix = rover_coords(obstcls_select)
    rocks_xpix, rocks_ypix = rover_coords(rocks_select)
    #6
    xpos, ypos, yaw = Rover.pos[0], Rover.pos[1], Rover.yaw
    terrain_x_world, terrain_y_world = pix_to_world(terrain_xpix, terrain_ypix, xpos, ypos, yaw, world_size,
                                                    world_scale)
    obstcls_x_world, obstcls_y_world = pix_to_world(obstcls_xpix, oobstcls_ypix, xpos, ypos, yaw, world_size,
                                                    world_scale)
    rocks_x_world, rocks_y_world = pix_to_world(rocks_xpix, rocks_ypix, xpos, ypos, yaw, world_size, world_scale)
    #7
    Rover.worldmap[terrain_y_world, terrain_x_world, 0] += 255
    Rover.worldmap[obstcls_y_world, obstcls_x_world, 2] += 255
    Rover.worldmap[rocks_y_world, rocks_x_world, 1] += 255
    #8
    terrain_dist, terrain_angles = to_polar_coords(terrain_xpix, terrain_ypix)
    rock_dist, rock_angles = to_polar_coords(rocks_xpix, rocks_ypix)
    obstcls_dist, obstcls_angles = to_polar_coords(obstcls_xpix, oobstcls_ypix)


    Rover.nav_dists, Rover.nav_angles = terrain_dist, terrain_angles
    Rover.rocks_dists, Rover.rocks_angles = rock_dist, rock_angles
    Rover.obstcls_dists, Rover.obstcls_angles = obstcls_dist, obstcls_angles

    return Rover