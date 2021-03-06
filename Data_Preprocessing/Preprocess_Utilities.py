import numpy as np
import matplotlib.pyplot as plt
import h5py

# given raw_image & road_img (road mask), return: raw_img patches, road mask, road existence
def create_labelled_patches(raw_image, road_img, 
                            row_offset = 0, column_offset = 0, step = 28, minimum_road_mark = 0.01):
    image_patch = []
    road_patch_coord = []
    road_existence = []

    i = row_offset
    while(i+step <= raw_image[0].shape[0]):
        j = column_offset
        while (j+step <= raw_image[0].shape[1]):
            cur_img_patch = raw_image[:,i:i+step, j:j+step]
            cur_road_patch = road_img[i:i+step, j:j+step]

            if (cur_img_patch != -9999).all():

                image_patch.append(cur_img_patch)
                road_patch_coord.append((i,j))
                road_existence.append(cur_road_patch.sum() >= minimum_road_mark*step*step)
            j += step
        i += step
    
    return image_patch, road_patch_coord, road_existence


def create_set_with_name(raw_image, combined_road_mask, step, divide, save_dir_path=None, name=None, save_img=True, h5f=None):
    if divide:
        # record the top-left coordinate of each possible patches & divide into pos/neg groups
        pos_topleft_coordinate = []
        neg_topleft_coordinate = []

        row_offset = 0
        while (row_offset + step <= raw_image.shape[1]):
            col_offset = 0
            while (col_offset + step <= raw_image.shape[2]):
                cur_img_patch = raw_image         [:,row_offset:row_offset+step, col_offset:col_offset+step]
                cur_road_mask = combined_road_mask[  row_offset:row_offset+step, col_offset:col_offset+step]

                if (cur_img_patch != -9999).all():
                    if cur_road_mask [int(step/2), int(step/2)] == 1: # positive example
                        pos_topleft_coordinate.append((row_offset, col_offset))
                    else: # negative example
                        neg_topleft_coordinate.append((row_offset, col_offset))
              
                col_offset += 1
            row_offset += 1

        pos_topleft_coordinate = np.array(pos_topleft_coordinate)
        neg_topleft_coordinate = np.array(neg_topleft_coordinate)
        print("pos coordinates' shape=", pos_topleft_coordinate.shape)
        print("neg coordinates' shape=", neg_topleft_coordinate.shape)

        # save set
        if h5f is None:
            h5_path = save_dir_path + name
            h5f = h5py.File(h5_path, 'w')

        h5f.create_dataset(name='positive_example', data=pos_topleft_coordinate)
        h5f.create_dataset(name='negative_example', data=neg_topleft_coordinate)
        if save_img:
            h5f.create_dataset(name='raw_image', data=raw_image)
            h5f.create_dataset(name='road_mask', data=combined_road_mask)
        try:
            h5f.close()
        except:
            print("not able to close", h5f)


    else:
        # record the top-left coordinate of each possible patches sequentially
        topleft_coordinate = []

        row_offset = 0
        while (row_offset + step <= raw_image.shape[1]):
            col_offset = 0
            while (col_offset + step <= raw_image.shape[2]):
                cur_img_patch = raw_image[:,row_offset:row_offset+step, col_offset:col_offset+step]

                if (cur_img_patch != -9999).all():
                    topleft_coordinate.append((row_offset, col_offset))

                col_offset += 1
            row_offset += 1

        topleft_coordinate = np.array(topleft_coordinate)
        print("coordinates' shape=", topleft_coordinate.shape)

        # save set
        if h5f is None:
            h5_path = save_dir_path + name
            h5f = h5py.File(h5_path, 'w')
        h5f.create_dataset(name='topleft_coordinate', data=topleft_coordinate)
        if save_img:
            h5f.create_dataset(name='raw_image', data=raw_image)
            h5f.create_dataset(name='road_mask', data=combined_road_mask)
        try:
            h5f.close()
        except:
            print("not able to close", h5f)

    print("saved into ", h5_path)

# create segmentation data set => determine to belong pos/neg by passed in func => used for FCN data
def create_segment_set_with_name(raw_image, combined_road_mask, size, step, divide, save_dir_path=None, name=None, save_img=True, h5f=None,
                                 is_pos_exmp=lambda rd_mask: True, is_valid_patch=lambda patch: (patch != -9999).all()):
    if divide:
        # record the top-left coordinate of each possible patches & divide into pos/neg groups
        pos_topleft_coordinate = []
        neg_topleft_coordinate = []

        row_offset = 0
        while (row_offset + size <= raw_image.shape[1]):
            col_offset = 0
            while (col_offset + size <= raw_image.shape[2]):
                cur_img_patch = raw_image         [:,row_offset:row_offset+size, col_offset:col_offset+size]
                cur_road_mask = combined_road_mask[  row_offset:row_offset+size, col_offset:col_offset+step]

                if is_valid_patch(cur_img_patch): # valid to be included into dataset
                    
                    if is_pos_exmp(cur_road_mask): # positive example
                        pos_topleft_coordinate.append((row_offset, col_offset))
                    else: # negative example
                        neg_topleft_coordinate.append((row_offset, col_offset))
              
                col_offset += step
            row_offset += step

        pos_topleft_coordinate = np.array(pos_topleft_coordinate)
        neg_topleft_coordinate = np.array(neg_topleft_coordinate)
        print("pos coordinates' shape=", pos_topleft_coordinate.shape)
        print("neg coordinates' shape=", neg_topleft_coordinate.shape)

        # save set
        if h5f is None:
            h5_path = save_dir_path + name
            h5f = h5py.File(h5_path, 'w')
        h5f.create_dataset(name='positive_example', data=pos_topleft_coordinate)
        h5f.create_dataset(name='negative_example', data=neg_topleft_coordinate)
        if save_img:
            h5f.create_dataset(name='raw_image', data=raw_image)
            h5f.create_dataset(name='road_mask', data=combined_road_mask)
        try:
            h5f.close()
        except:
            print("not able to close", h5f)
            
    else:
        # record the top-left coordinate of each possible patches sequentially
        topleft_coordinate = []

        row_offset = 0
        while (row_offset + size <= raw_image.shape[1]):
            col_offset = 0
            while (col_offset + size <= raw_image.shape[2]):
                cur_img_patch = raw_image         [:,row_offset:row_offset+size, col_offset:col_offset+size]
                cur_road_mask = combined_road_mask[  row_offset:row_offset+size, col_offset:col_offset+step]

                if is_valid_patch(cur_img_patch): # valid to be included into dataset
                    topleft_coordinate.append((row_offset, col_offset))
              
                col_offset += step
            row_offset += step

        topleft_coordinate = np.array(topleft_coordinate)
        print("coordinates' shape=", topleft_coordinate.shape)

        # save set
        if h5f is None:
            h5_path = save_dir_path + name
            h5f = h5py.File(h5_path, 'w')
        h5f.create_dataset(name='coordinates', data=topleft_coordinate)
        if save_img:
            h5f.create_dataset(name='raw_image', data=raw_image)
            h5f.create_dataset(name='road_mask', data=combined_road_mask)
        try:
            h5f.close()
        except:
            print("not able to close", h5f)


    print("saved into ", h5_path)