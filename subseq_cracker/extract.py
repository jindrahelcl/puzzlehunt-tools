#!/usr/bin/env python3

import os
import argparse
import logging
import pandas as pd
import osmium as osm
import pickle

class AreaHandler(osm.SimpleHandler):
    def __init__(self, tl, br, nodes_only=False, skip_nodes=False, debug=False):
        super(AreaHandler, self).__init__()
        self.nodes = []
        self.csv_columns = ["id", "type", "name", "lat", "lon"]
        self.csv = {c : [] for c in self.csv_columns}
        self.debug = debug
        self.names = set()
        self.top_left = tl
        self.bottom_right = br
        self.idx = {}
        self.nodes_only = nodes_only
        self.skip_nodes = skip_nodes
        self.n = 0
        self.w = 0
        self.a = 0

    def _is_node_inside(self, lat, lon):
        return (self.bottom_right[0] < lat < self.top_left[0] 
                and self.top_left[1] < lon < self.bottom_right[1])


    def _is_way_inside(self, way):
        if not hasattr(way, "nodes") or not way.nodes:
            return False

        for node_ref in way.nodes:
            loc = self.idx.get(node_ref.ref)

            if not self._is_node_inside(lat=loc[0], lon=loc[1]):
                return False
        return True


    def _is_area_inside(self, area):
        if not hasattr(area, "outer_rings"):
            return False

        for outer_ring in area.outer_rings():
            for node_ref in outer_ring:
                loc = self.idx.get(node_ref.ref)

                if not self._is_node_inside(lat=loc[0], lon=loc[1]):
                    return False
        return True

    def node(self, o):
        if self.skip_nodes:
            return

        self.n += 1

        if self.n % 1000000 == 0:
            logger.info(f"{self.n} nodes processed")

        node_lat = o.location.lat
        node_lon = o.location.lon

        self.idx[o.id] = (o.location.lat, o.location.lon)

        if not 'name' in o.tags\
            or o.tags["name"] in self.names\
            or len(o.tags["name"]) < 5\
            or o.deleted:
            return

        name = o.tags["name"]
        self.names.add(name)

        if self._is_node_inside(lat=node_lat, lon=node_lon):
            self.csv["id"].append(o.id)
            self.csv["name"].append(name)
            self.csv["type"].append("node")
            self.csv["lat"].append(node_lat)
            self.csv["lon"].append(node_lon)

            logger.info("[NODE] " + name)


    def way(self, o):
        if self.nodes_only:
            return

        self.w += 1

        if self.w % 10000 == 0:
            logger.info(f"{self.w} ways processed")

        if not 'name' in o.tags\
            or o.tags["name"] in self.names\
            or len(o.tags["name"]) < 5\
            or o.deleted:
            return

        name = o.tags["name"]
        self.names.add(name)

        if self._is_way_inside(o):

            loc = self.idx.get(o.nodes[0].ref)
            self.csv["id"].append(o.id)
            self.csv["name"].append(name)
            self.csv["type"].append("way")
            self.csv["lat"].append(loc[0])
            self.csv["lon"].append(loc[1])

            logger.info("[WAY] " + name)


    def area(self, o):
        if self.nodes_only:
            return

        self.a += 1

        if self.a % 10000 == 0:
            logger.info(f"{self.a} areas processed")

        if not 'name' in o.tags\
            or o.tags["name"] in self.names\
            or len(o.tags["name"]) < 5\
            or not o.visible\
            or o.deleted:
            return

        name = o.tags["name"]
        self.names.add(name)

        if self._is_area_inside(o):
            outer_ring = next(o.outer_rings())
            loc = self.idx.get(outer_ring[0].ref)
            self.csv["id"].append(o.id)
            self.csv["name"].append(name)
            self.csv["type"].append("area")
            self.csv["lat"].append(loc[0])
            self.csv["lon"].append(loc[1])

            logger.info("[AREA] " + name)



logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    areas = {
        "praha" :  ((50.1565342, 14.2586031), (49.9938864, 14.6248239)),
        "brno" :  ((49.2952, 16.3937), (49.0909, 16.8091))
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", type=str, default="czech-republic-latest.osm.pbf",
        help="Path to an OSM dump in PBF format.")
    parser.add_argument("-o", "--output_file", type=str, required=True,
        help="Output CSV with names of places.")
    parser.add_argument("-a", "--area", type=str, required=True,
        help=f"Which area to process, options: {areas.keys()}")
    parser.add_argument("-n", "--nodes_only", action="store_true",
        help="Use if you only want to create node cache (later to be used by ways and areas)")
    parser.add_argument("-s", "--skip_nodes", action="store_true",
        help="Use if you only want to process ways and areas (using existing node cache)")
    parser.add_argument("-d", "--debug", action="store_true")

    args = parser.parse_args()
    logger.info(args)
    
    top_left, bottom_right = areas[args.area.lower()]

    h = AreaHandler(
        tl=top_left, 
        br=bottom_right, 
        nodes_only=args.nodes_only, 
        skip_nodes=args.skip_nodes, 
        debug=args.debug
    )

    node_cache = f'node_cache_{args.area}'
    if os.path.exists(node_cache):
        with open(node_cache, 'rb') as f:
            idx = pickle.load(f)
            h.idx = idx

        logger.info("Node cache loaded")

    h.apply_file(args.input_file)

    with open(node_cache, "wb") as f:
        pickle.dump(h.idx, f)

    df = pd.DataFrame(h.csv)
    df.to_csv(args.output_file, index=False, header=True)
