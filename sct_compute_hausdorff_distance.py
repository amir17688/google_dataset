#!/usr/bin/env python
#
# Thinning with the Zhang-Suen algorithm (1984) --> code taken from  https://github.com/linbojin/Skeletonization-by-Zhang-Suen-Thinning-Algorithm
# Computation of the distances between two skeleton
# ---------------------------------------------------------------------------------------
# Copyright (c) 2013 Polytechnique Montreal <www.neuro.polymtl.ca>
# Authors: Sara Dupont
# CREATED: 2015-07-15
#
# About the license: see the file LICENSE.TXT
#########################################################################################

import sys
import time
import os
import numpy as np
import sct_utils as sct
from msct_image import Image, get_dimension
from sct_image import set_orientation
from msct_parser import Parser
import msct_gmseg_utils as sct_gm


# TODO: display results ==> not only max : with a violin plot of h1 and h2 distribution ? see dev/straightening --> seaborn.violinplot
# TODO: add the option Hyberbolic Hausdorff's distance : see  choi and seidel paper

# ----------------------------------------------------------------------------------------------------------------------
# PARAM ----------------------------------------------------------------------------------------------------------------
class Param:
    def __init__(self):
        self.debug = 0
        self.thinning = True
        self.verbose = 1


# ----------------------------------------------------------------------------------------------------------------------
# THINNING -------------------------------------------------------------------------------------------------------------
class Thinning:
    def __init__(self, im, v=1):
        sct.printv('Thinning ... ', v, 'normal')
        self.image = im
        self.image.data = bin_data(self.image.data)
        self.dim_im = len(self.image.data.shape)

        if self.dim_im == 2:
            self.thinned_image = Image(param=self.zhang_suen(self.image.data), absolutepath=self.image.path + self.image.file_name + '_thinned' + self.image.ext, hdr=self.image.hdr)

        elif self.dim_im == 3:
            assert self.image.orientation == 'IRP'

            thinned_data = np.asarray([self.zhang_suen(im_slice) for im_slice in self.image.data])

            self.thinned_image = Image(param=thinned_data, absolutepath=self.image.path + self.image.file_name + '_thinned' + self.image.ext, hdr=self.image.hdr)

    # ------------------------------------------------------------------------------------------------------------------
    def get_neighbours(self, x, y, image):
        """
        Return 8-neighbours of image point P1(x,y), in a clockwise order
        code from https://github.com/linbojin/Skeletonization-by-Zhang-Suen-Thinning-Algorithm
        :param x:
        :param y:
        :param image:
        :return:
        """
        # now = time.time()
        x_1, y_1, x1, y1 = x-1, y-1, x+1, y+1
        neighbours = [image[x_1][y], image[x_1][y1], image[x][y1], image[x1][y1],     # P2,P3,P4,P5
                      image[x1][y], image[x1][y_1], image[x][y_1], image[x_1][y_1]]    # P6,P7,P8,P9
        # t = time.time() - now
        # print 't neighbours: ', t
        return neighbours

    # ------------------------------------------------------------------------------------------------------------------
    def transitions(self, neighbours):
        """
        No. of 0,1 patterns (transitions from 0 to 1) in the ordered sequence
        code from https://github.com/linbojin/Skeletonization-by-Zhang-Suen-Thinning-Algorithm
        :param neighbours:
        :return:
        """
        # now = time.time()
        n = neighbours + neighbours[0:1]      # P2, P3, ... , P8, P9, P2
        s = np.sum((n1, n2) == (0, 1) for n1, n2 in zip(n, n[1:]))  # (P2,P3), (P3,P4), ... , (P8,P9), (P9,P2)
        # t = time.time() - now
        # print 't transitions sum: ', t
        return s

    # ------------------------------------------------------------------------------------------------------------------
    def zhang_suen(self, image):
        """
        the Zhang-Suen Thinning Algorithm
        code from https://github.com/linbojin/Skeletonization-by-Zhang-Suen-Thinning-Algorithm
        :param image:
        :return:
        """
        # now = time.time()
        image_thinned = image.copy()  # deepcopy to protect the original image
        changing1 = changing2 = 1  # the points to be removed (set as 0)
        while changing1 or changing2:  # iterates until no further changes occur in the image
            # Step 1
            changing1 = []
            max = len(image_thinned) - 1
            pass_list = [1, max]
            # rows, columns = image_thinned.shape  # x for rows, y for columns

            # for x in range(1, rows - 1):         # No. of  rows
            # for y in range(1, columns - 1):  # No. of columns
            for x, y in non_zero_coord(image_thinned):
                if x not in pass_list and y not in pass_list:
                    # if image_thinned[x][y] == 1:  # Condition 0: Point P1 in the object regions
                    P2, P3, P4, P5, P6, P7, P8, P9 = n = self.get_neighbours(x, y, image_thinned)
                    if (2 <= sum(n) <= 6 and    # Condition 1: 2<= N(P1) <= 6
                        P2 * P4 * P6 == 0 and    # Condition 3
                        P4 * P6 * P8 == 0 and   # Condition 4
                        self.transitions(n) == 1):    # Condition 2: S(P1)=1
                        changing1.append((x, y))
            for x, y in changing1:
                image_thinned[x][y] = 0
            # Step 2
            changing2 = []

            # for x in range(1, rows - 1):
            # for y in range(1, columns - 1):
            for x, y in non_zero_coord(image_thinned):
                if x not in pass_list and y not in pass_list:
                    # if image_thinned[x][y] == 1:  # Condition 0
                    P2, P3, P4, P5, P6, P7, P8, P9 = n = self.get_neighbours(x, y, image_thinned)
                    if (2 <= sum(n) <= 6 and       # Condition 1
                        P2 * P4 * P8 == 0 and       # Condition 3
                        P2 * P6 * P8 == 0 and  # Condition 4
                        self.transitions(n) == 1):    # Condition 2
                        changing2.append((x, y))
            for x, y in changing2:
                image_thinned[x][y] = 0
        # t = time.time() - now
        # print 't thinning: ', t
        return image_thinned


# ----------------------------------------------------------------------------------------------------------------------
# HAUSDORFF'S DISTANCE -------------------------------------------------------------------------------------------------
class HausdorffDistance:
    def __init__(self, data1, data2, v=1):
        """
        the hausdorff distance between two sets is the maximum of the distances from a point in any of the sets to the nearest point in the other set
        :return:
        """
        # now = time.time()
        sct.printv('Computing 2D Hausdorff\'s distance ... ', v, 'normal')
        self.data1 = bin_data(data1)
        self.data2 = bin_data(data2)

        self.min_distances_1 = self.relative_hausdorff_dist(self.data1, self.data2, v)
        self.min_distances_2 = self.relative_hausdorff_dist(self.data2, self.data1, v)

        # relatives hausdorff's distances in pixel
        self.h1 = np.max(self.min_distances_1)
        self.h2 = np.max(self.min_distances_2)

        # Hausdorff's distance in pixel
        self.H = max(self.h1, self.h2)
        # t = time.time() - now
        # print 'Hausdorff dist time :', t

    # ------------------------------------------------------------------------------------------------------------------
    def relative_hausdorff_dist(self, dat1, dat2, v=1):
        h = np.zeros(dat1.shape)
        nz_coord_1 = non_zero_coord(dat1)
        nz_coord_2 = non_zero_coord(dat2)
        if len(nz_coord_1) != 0 and len(nz_coord_2) != 0 :
            for x1, y1 in nz_coord_1:
                # for x1 in range(dat1.shape[0]):
                # for y1 in range(dat1.shape[1]):
                # if dat1[x1, y1] == 1:
                d_p1_dat2 = []
                p1 = np.asarray([x1, y1])
                for x2, y2 in nz_coord_2:
                    # for x2 in range(dat2.shape[0]):
                    # for y2 in range(dat2.shape[1]):
                    # if dat2[x2, y2] == 1:
                    p2 = np.asarray([x2, y2])
                    d_p1_dat2.append(np.linalg.norm(p1-p2))  # Euclidean distance between p1 and p2
                h[x1, y1] = min(d_p1_dat2)
        else:
            sct.printv('Warning: an image is empty', v, 'warning')
        return h


# ----------------------------------------------------------------------------------------------------------------------
# COMPUTE DISTANCES ----------------------------------------------------------------------------------------------------
class ComputeDistances:
    def __init__(self, im1, im2=None, param=None):
        self.im1 = im1
        self.im2 = im2
        self.dim_im = len(self.im1.data.shape)
        self.dim_pix = 0
        self.distances = None
        self.res = ''
        self.param = param
        self.dist1_distribution = None
        self.dist2_distribution = None

        if self.dim_im == 3:
            self.orientation1 = self.im1.orientation
            if self.orientation1 != 'IRP':
                self.im1 = set_orientation(self.im1, 'IRP')

            if self.im2 is not None:
                self.orientation2 = self.im2.orientation
                if self.orientation2 != 'IRP':
                    self.im2 = set_orientation(self.im2, 'IRP')

        if self.param.thinning:
            self.thinning1 = Thinning(self.im1, self.param.verbose)
            self.thinning1.thinned_image.save()

            if self.im2 is not None:
                self.thinning2 = Thinning(self.im2, self.param.verbose)
                self.thinning2.thinned_image.save()

        if self.dim_im == 2 and self.im2 is not None:
            self.compute_dist_2im_2d()

        if self.dim_im == 3:
            if self.im2 is None:
                self.compute_dist_1im_3d()
            else:
                self.compute_dist_2im_3d()

        if self.dim_im == 2 and self.distances is not None:
            self.dist1_distribution = self.distances.min_distances_1[np.nonzero(self.distances.min_distances_1)]
            self.dist2_distribution = self.distances.min_distances_2[np.nonzero(self.distances.min_distances_2)]
        if self.dim_im == 3:
            self.dist1_distribution = []
            self.dist2_distribution = []
            for d in self.distances:
                self.dist1_distribution.append(d.min_distances_1[np.nonzero(d.min_distances_1)])
                self.dist2_distribution.append(d.min_distances_2[np.nonzero(d.min_distances_2)])

            self.res = 'Hausdorff\'s distance  -  First relative Hausdorff\'s distance median - Second relative Hausdorff\'s distance median(all in mm)\n'
            for i, d in enumerate(self.distances):
                med1 = np.median(self.dist1_distribution[i])
                med2 = np.median(self.dist2_distribution[i])
                if self.im2 is None:
                    self.res += 'Slice ' + str(i) + ' - slice ' + str(i+1) + ': ' + str(d.H*self.dim_pix) + '  -  ' + str(med1*self.dim_pix) + '  -  ' + str(med2*self.dim_pix) + ' \n'
                else:
                    self.res += 'Slice ' + str(i) + ': ' + str(d.H*self.dim_pix) + '  -  ' + str(med1*self.dim_pix) + '  -  ' + str(med2*self.dim_pix) + ' \n'

        sct.printv('-----------------------------------------------------------------------------\n' +
                   self.res, self.param.verbose, 'normal')

        if self.param.verbose == 2:
            self.show_results()

    # ------------------------------------------------------------------------------------------------------------------
    def compute_dist_2im_2d(self):
        nx1, ny1, nz1, nt1, px1, py1, pz1, pt1 = get_dimension(self.im1)
        nx2, ny2, nz2, nt2, px2, py2, pz2, pt2 = get_dimension(self.im2)
        assert px1 == px2 and py1 == py2 and px1 == py1
        self.dim_pix = py1

        if self.param.thinning:
            dat1 = self.thinning1.thinned_image.data
            dat2 = self.thinning2.thinned_image.data
        else:
            dat1 = bin_data(self.im1.data)
            dat2 = bin_data(self.im2.data)

        self.distances = HausdorffDistance(dat1, dat2, self.param.verbose)
        self.res = 'Hausdorff\'s distance : ' + str(self.distances.H*self.dim_pix) + ' mm\n\n' \
                   'First relative Hausdorff\'s distance : ' + str(self.distances.h1*self.dim_pix) + ' mm\n' \
                   'Second relative Hausdorff\'s distance : ' + str(self.distances.h2*self.dim_pix) + ' mm'

    # ------------------------------------------------------------------------------------------------------------------
    def compute_dist_1im_3d(self):
        nx1, ny1, nz1, nt1, px1, py1, pz1, pt1 = get_dimension(self.im1)
        self.dim_pix = py1

        if self.param.thinning:
            dat1 = self.thinning1.thinned_image.data
        else:
            dat1 = bin_data(self.im1.data)

        self.distances = []
        for i, dat_slice in enumerate(dat1[:-1]):
            self.distances.append(HausdorffDistance(bin_data(dat_slice), bin_data(dat1[i+1]), self.param.verbose))

    # ------------------------------------------------------------------------------------------------------------------
    def compute_dist_2im_3d(self):
        nx1, ny1, nz1, nt1, px1, py1, pz1, pt1 = get_dimension(self.im1)
        nx2, ny2, nz2, nt2, px2, py2, pz2, pt2 = get_dimension(self.im2)
        assert round(pz1, 5) == round(pz2, 5) and round(py1, 5) == round(py2, 5)
        assert nx1 == nx2
        self.dim_pix = py1

        if self.param.thinning:
            dat1 = self.thinning1.thinned_image.data
            dat2 = self.thinning2.thinned_image.data
        else:
            dat1 = bin_data(self.im1.data)
            dat2 = bin_data(self.im2.data)

        self.distances = []
        for slice1, slice2 in zip(dat1, dat2):
            self.distances.append(HausdorffDistance(slice1, slice2, self.param.verbose))

    # ------------------------------------------------------------------------------------------------------------------
    def show_results(self):
        import seaborn as sns
        import matplotlib.pyplot as plt
        import pandas as pd
        plt.hold(True)
        sns.set(style="whitegrid", palette="pastel", color_codes=True)
        plt.figure(figsize=(35, 20))

        data_dist = {"distances": [], "image": [], "slice": []}

        if self.dim_im == 2:
            data_dist["distances"].append([dist*self.dim_pix for dist in self.dist1_distribution])
            data_dist["image"].append(len(self.dist1_distribution)*[1])
            data_dist["slice"].append(len(self.dist1_distribution)*[0])

            data_dist["distances"].append([dist*self.dim_pix for dist in self.dist2_distribution])
            data_dist["image"].append(len(self.dist2_distribution)*[2])
            data_dist["slice"].append(len(self.dist2_distribution)*[0])

        if self.dim_im == 3:
            for i in range(len(self.distances)):
                data_dist["distances"].append([dist*self.dim_pix for dist in self.dist1_distribution[i]])
                data_dist["image"].append(len(self.dist1_distribution[i])*[1])
                data_dist["slice"].append(len(self.dist1_distribution[i])*[i])
                data_dist["distances"].append([dist*self.dim_pix for dist in self.dist2_distribution[i]])
                data_dist["image"].append(len(self.dist2_distribution[i])*[2])
                data_dist["slice"].append(len(self.dist2_distribution[i])*[i])

        for k in data_dist.keys():  # flatten the lists in data_dist
            data_dist[k] = [item for sublist in data_dist[k] for item in sublist]

        data_dist = pd.DataFrame(data_dist)
        sns.violinplot(x="slice", y="distances", hue="image", data=data_dist, split=True, inner="point", cut=0)
        plt.savefig('violin_plot.png')
        # plt.show()


# ----------------------------------------------------------------------------------------------------------------------
def bin_data(data):
    return np.asarray((data > 0).astype(int))


# ----------------------------------------------------------------------------------------------------------------------
def non_zero_coord(data):
    dim = len(data.shape)
    if dim == 3:
        X, Y, Z = (data > 0).nonzero()
        list_coordinates = [(X[i], Y[i], Z[i]) for i in range(0, len(X))]
    elif dim == 2:
        X, Y = (data > 0).nonzero()
        list_coordinates = [(X[i], Y[i]) for i in range(0, len(X))]
    return list_coordinates


def get_parser():
    # Initialize the parser
    parser = Parser(__file__)
    parser.usage.set_description('Compute the Hausdorff\'s distance between two binary images which can be thinned (ie skeletonized)'
                                 'If only one image is inputted, it will be only thinned')
    parser.add_option(name="-i",
                      type_value="file",
                      description="First Image on which you want to find the skeleton",
                      mandatory=True,
                      example='t2star_manual_gmseg.nii.gz')
    parser.add_option(name="-d",
                      type_value="file",
                      description="Second Image on which you want to find the skeleton",
                      mandatory=False,
                      default_value=None,
                      example='t2star_manual_gmseg.nii.gz')
    parser.add_option(name="-r",
                      type_value=None,
                      description="Second Image on which you want to find the skeleton",
                      mandatory=False,
                      deprecated_by='-d')
    parser.add_option(name="-thinning",
                      type_value="multiple_choice",
                      description="Thinning : find the skeleton of the binary images using the Zhang-Suen algorithm (1984) and use it to compute the hausdorff's distance",
                      mandatory=False,
                      default_value=1,
                      example=['0', '1'])
    parser.add_option(name="-t",
                      type_value=None,
                      description="Thinning : find the skeleton of the binary images using the Zhang-Suen algorithm (1984) and use it to compute the hausdorff's distance",
                      deprecated_by="-thinning",
                      mandatory=False)
    parser.add_option(name="-resampling",
                      type_value="float",
                      description="pixel size in mm to resample to",
                      mandatory=False,
                      default_value=0.1,
                      example=0.5)
    parser.add_option(name="-o",
                      type_value="file_output",
                      description="Name of the output file",
                      mandatory=False,
                      default_value='hausdorff_distance.txt',
                      example='my_hausdorff_dist.txt')
    parser.add_option(name="-v",
                      type_value="int",
                      description="verbose: 0 = nothing, 1 = classic, 2 = expended",
                      mandatory=False,
                      default_value=0,
                      example='1')
    return parser

########################################################################################################################
# ------------------------------------------------------  MAIN ------------------------------------------------------- #
########################################################################################################################

if __name__ == "__main__":
    param = Param()
    input_fname = None
    if param.debug:
        print '\n*** WARNING: DEBUG MODE ON ***\n'
    else:
        param_default = Param()
        parser = get_parser()

        arguments = parser.parse(sys.argv[1:])
        input_fname = arguments["-i"]
        input_second_fname = ''
        output_fname = 'hausdorff_distance.txt'
        resample_to = 0.1

        if "-d" in arguments:
            input_second_fname = arguments["-d"]
        if "-thinning" in arguments:
            param.thinning = bool(int(arguments["-thinning"]))
        if "-resampling" in arguments:
            resample_to = arguments["-resampling"]
        if "-o" in arguments:
            output_fname = arguments["-o"]
        if "-v" in arguments:
            param.verbose = int(arguments["-v"])

        tmp_dir = 'tmp_' + time.strftime("%y%m%d%H%M%S")
        sct.run('mkdir ' + tmp_dir)
        im1_name = "im1.nii.gz"
        sct.run('cp ' + input_fname + ' ' + tmp_dir + '/' + im1_name)
        if input_second_fname != '':
            im2_name = 'im2.nii.gz'
            sct.run('cp ' + input_second_fname + ' ' + tmp_dir + '/' + im2_name)
        else:
            im2_name = None

        os.chdir(tmp_dir)
        # now = time.time()
        input_im1 = Image(sct_gm.resample_image(im1_name, binary=True, thr=0.5, npx=resample_to, npy=resample_to))
        if im2_name is not None:
            input_im2 = Image(sct_gm.resample_image(im2_name, binary=True, thr=0.5, npx=resample_to, npy=resample_to))
        else:
            input_im2 = None

        computation = ComputeDistances(input_im1, im2=input_im2, param=param)
        res_fic = open('../' + output_fname, 'w')
        res_fic.write(computation.res)
        res_fic.write('\n\nInput 1: ' + input_fname)
        res_fic.write('\nInput 2: ' + input_second_fname)
        res_fic.close()

        #TODO change back the orientatin of the thinned image
        if param.thinning:
            sct.run('cp ' + computation.thinning1.thinned_image.file_name + computation.thinning1.thinned_image.ext + ' ../' + sct.extract_fname(input_fname)[1] + '_thinned' + sct.extract_fname(input_fname)[2])
            if im2_name is not None:
                sct.run('cp ' + computation.thinning2.thinned_image.file_name + computation.thinning2.thinned_image.ext + ' ../' + sct.extract_fname(input_second_fname)[1] + '_thinned' + sct.extract_fname(input_second_fname)[2])

        os.chdir('..')
        # print 'Total time: ', time.time() - now