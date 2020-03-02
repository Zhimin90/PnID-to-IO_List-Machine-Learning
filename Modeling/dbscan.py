# -*- coding: utf-8 -*-
"""
This is a simple implementation of DBSCAN intended to explain the algorithm.

@author: Chris McCormick
"""
"""
Modified by: Zhimin Zou
Modified original McCormick's code. Altered DBSCAN algorithm to have a maximum 
density for each cluster. When growing each cluster, if max density has been reached, 
the Breadth first search stops and returns search points for the next cluster to group.
"""

import numpy

def MyDBSCAN(D, eps, MinPts, MaxPts):
    """
    Cluster the dataset `D` using the DBSCAN algorithm.
    
    MyDBSCAN takes a dataset `D` (a list of vectors), a threshold distance
    `eps`, and a required number of points `MinPts`.
    
    It will return a list of cluster labels. The label -1 means noise, and then
    the clusters are numbered starting from 1.
    """
 
    # This list will hold the final cluster assignment for each point in D.
    # There are two reserved values:
    #    -1 - Indicates a noise point
    #     0 - Means the point hasn't been considered yet.
    # Initially all labels are 0.    
    labels = [0]*len(D)

    # C is the ID of the current cluster.    
    C = 0
    clusterDict = {}
    NeighborPts = []

    # This outer loop is just responsible for picking new seed points--a point
    # from which to grow a new cluster.
    # Once a valid seed point is found, a new cluster is created, and the 
    # cluster growth is all handled by the 'expandCluster' routine.
    
    # For each point P in the Dataset D...
    # ('P' is the index of the datapoint, rather than the datapoint itself.)
    for P in range(0, len(D)):
    
        # Only points that have not already been claimed can be picked as new 
        # seed points.    
        # If the point's label is not 0, continue to the next point.
        if not (labels[P] == 0):
           continue
        
        

        # Find all of P's neighboring points.
        append_list = regionQuery(D, P, eps)

        setNeighborPts = set(NeighborPts) #remove duplicate points
        for NeighborPt in append_list:
            if NeighborPt in setNeighborPts:
                continue
            else:
                NeighborPts += [NeighborPt]

        #print("Neighbors Quried: " + str(NeighborPts))
        
        # If the number is below MinPts, this point is noise. 
        # This is the only condition under which a point is labeled 
        # NOISE--when it's not a valid seed point. A NOISE point may later 
        # be picked up by another cluster as a boundary point (this is the only
        # condition under which a cluster label can change--from NOISE to 
        # something else).
        if len(NeighborPts) < MinPts:
            labels[P] = -1
            #labels[P] = labels[P]
        # Otherwise, if there are at least MinPts nearby, use this point as the 
        # seed for a new cluster.    
        else: 
            C += 1
            clusterDict[C] = 1
            #growCluster returns unprocessed NeighborPts back for new cluster assignment
            append_list = growCluster(clusterDict, D, labels, P, NeighborPts, C, eps, MinPts, MaxPts)
            setNeighborPts = set(NeighborPts)
            for NeighborPt in append_list:
                if NeighborPt in setNeighborPts:
                    continue
                else:
                    NeighborPts += [NeighborPt]
    # All data has been clustered!
    return labels


def growCluster(clusterDict, D, labels, P, NeighborPts, C, eps, MinPts, MaxPts):
    """
    Grow a new cluster with label `C` from the seed point `P`.
    
    This function searches through the dataset to find all points that belong
    to this new cluster. When this function returns, cluster `C` is complete.
    
    Parameters:
      `D`      - The dataset (a list of vectors)
      `labels` - List storing the cluster labels for all dataset points
      `P`      - Index of the seed point for this new cluster
      `NeighborPts` - All of the neighbors of `P`
      `C`      - The label for this new cluster.  
      `eps`    - Threshold distance
      `MinPts` - Minimum required number of neighbors
    """

    # Assign the cluster label to the seed point.
    print("Growing Cluster")
    #print("Current Dictionary is: "+ str(clusterDict))
    labels[P] = C
    if C in clusterDict.keys():
        clusterDict[C] += 1
    else:
        print("fault")
        #clusterDict[label] = 1

    # Look at each neighbor of P (neighbors are referred to as Pn). 
    # NeighborPts will be used as a FIFO queue of points to search--that is, it
    # will grow as we discover new branch points for the cluster. The FIFO
    # behavior is accomplished by using a while-loop rather than a for-loop.
    # In NeighborPts, the points are represented by their index in the original
    # dataset.
    i = 0
    while (i < len(NeighborPts)):    
        
        # Get the next point from the queue.        
        Pn = NeighborPts[i]
       
        # If Pn was labelled NOISE during the seed search, then we
        # know it's not a branch point (it doesn't have enough neighbors), so
        # make it a leaf point of cluster C and move on.
        if labels[Pn] == -1:
           labels[Pn] = C
        
        # Otherwise, if Pn isn't already claimed, claim it as part of C.
        elif labels[Pn] == 0:
            # Add Pn to cluster C (Assign cluster label C).
            labels[Pn] = C
            if C in clusterDict.keys():
                clusterDict[C] += 1
            else:
                print("fault")
                #clusterDict[label] = 1

            # Find all the neighbors of Pn
            PnNeighborPts = regionQuery(D, Pn, eps)
            
            # If Pn has at least MinPts neighbors, it's a branch point!
            # Add all of its neighbors to the FIFO queue to be searched. 
            #if (len(PnNeighborPts) >= MinPts) and (len(PnNeighborPts) < MaxPts):
            if (len(PnNeighborPts) >= MinPts):
                NeighborPts = NeighborPts + PnNeighborPts
            # If Pn *doesn't* have enough neighbors, then it's a leaf point.
            # Don't queue up it's neighbors as expansion points.
            #else:
                # Do nothing                
                #NeighborPts = NeighborPts               
        
        # Advance to the next point in the FIFO queue.
        if clusterDict[C] <= MaxPts:
            i += 1
        else:
            #print(NeighborPts[i+1:])
            return NeighborPts[i:]        
    print("Completed")
    return []
    # We've finished growing cluster C!


def regionQuery(D, P, eps):
    """
    Find all points in dataset `D` within distance `eps` of point `P`.
    
    This function calculates the distance between a point P and every other 
    point in the dataset, and then returns only those points which are within a
    threshold distance `eps`.
    """
    neighbors = []
    
    # For each point in the dataset...
    for Pn in range(0, len(D)):
        
        # If the distance is below the threshold, add it to the neighbors list.
        if numpy.linalg.norm(D[P] - D[Pn]) < eps:
           neighbors.append(Pn)
            
    return neighbors