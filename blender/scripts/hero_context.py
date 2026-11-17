"""Shared context for the modular VERDANT MARKET scene builders."""
from __future__ import annotations
import json
from pathlib import Path

import bpy
from hero_utils import ROOT, TEXTURES, ensure_collection, surface, emissive, texture_surface, hex_linear

class HeroBuilder:
    def __init__(self, scene: bpy.types.Scene, config: dict):
        self.scene=scene; self.config=config
        self.collections={}
        self.materials={}
        self.texture_catalog=json.loads((TEXTURES/"packaging_catalog.json").read_text(encoding="utf-8"))
        self.textures={}
        self.product_templates={}
        self.web_source_objects=[]
        self.label_positions={}
        self.web_label_names=set()
        self.scene["project"]="VERDANT MARKET — Intelligent Retail Environment"
        self.scene["render_role"]="Cinematic presentation only; not used for spectral or ROI measurements."
        self.scene["research_boundary"]="Blender Cycles is RGB rendering. D65/LED spectral calculations remain in the Python colour pipeline."

    def collection(self, name: str, hidden=False):
        if name not in self.collections:
            self.collections[name]=ensure_collection(self.scene,name,hidden=hidden)
        return self.collections[name]

    def mat(self, name: str, color: str, roughness=.42, metallic=0.0, **kwargs):
        if name not in self.materials:
            self.materials[name]=surface(name,color,roughness,metallic,**kwargs)
        return self.materials[name]

    def emit(self, name: str, color: str, strength=1.0):
        if name not in self.materials:self.materials[name]=emissive(name,color,strength)
        return self.materials[name]

    def texture_path(self, key: str, variant: int=0) -> Path:
        paths=self.texture_catalog[key]
        return ROOT / paths[variant % len(paths)]

    def image_mat(self, name: str, key: str, variant=0, roughness=.52, bump_strength=.12):
        cache=f"texture::{name}::{key}::{variant}"
        if cache not in self.materials:
            self.materials[cache]=texture_surface(name,self.texture_path(key,variant),roughness,bump_strength=bump_strength)
        return self.materials[cache]

    def configured_colour(self, colour_id: str) -> str:
        return self.config["colours"][colour_id]["hex"]

    def mark_web(self, obj):
        obj["web_export"]=True
        self.web_source_objects.append(obj)
        return obj
