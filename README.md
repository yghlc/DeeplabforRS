# DeeplabforRS

We currently develop our codes for large areas in another repo: [Landuse_DL](https://github.com/yghlc/Landuse_DL), please check this repo for updates.

## Introduction
This repo contains codes for mapping thermokarst landform on remote sensing images based on [DeepLab V2](http://liangchiehchen.com/projects/DeepLab.html), which is a segmentation algorithm using Deep Convolutional Neural Network. If any code here is useful for your project, please consider citing [our paper](https://www.mdpi.com/2072-4292/10/12/2067):

```
@article{huang2018automatic,
  title={Automatic Mapping of Thermokarst Landforms from Remote Sensing Images Using Deep Learning: A Case Study in the Northeastern Tibetan Plateau},
  author={Huang, Lingcao and Liu, Lin and Jiang, Liming and Zhang, Tingjun},
  journal={Remote Sensing},
  volume={10},
  number={12},
  pages={2067},
  year={2018},
  publisher={Multidisciplinary Digital Publishing Institute}
}
```

## Disclaimer
This is a personal repo that we developed in the past. Some codes, including pre-processing and post-processing of remote sensing images may be useful for handling similar data. If you want to repeat our results in the paper, installing [DeepLab V2](http://liangchiehchen.com/projects/DeepLab.html) is necessary but painful. Since DeepLab has a newer version, i.e., [DeepLabV3+](https://github.com/tensorflow/models/tree/master/research/deeplab), we will use the new version in our future work. If we use your codes without adding a reference, please let us know. 


## TODO
We will update some of the codes, including bug fix and enhancement because they are used in other projects. 
If many requests (at least 10) to repeat our results, we will provide a docker distribution and demo. 
