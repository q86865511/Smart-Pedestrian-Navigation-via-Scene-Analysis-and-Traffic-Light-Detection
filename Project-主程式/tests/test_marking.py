"""marking.py 連通區域分析的純邏輯測試（只需 Pillow）。

重點是驗證「一次 analyzeRegions 取代原本三次 BFS」之後，
judgeFloor / drawCenter / drawArrow 得到的答案與各自單獨計算時相同。
"""
import sys
import types

from PIL import Image

# marking 只在命令列入口 test() 用到 cv2，純邏輯測試不必安裝 OpenCV
sys.modules.setdefault('cv2', types.ModuleType('cv2'))

import marking


ROAD = marking.targetColors[0]
BACKGROUND = (70, 70, 70)


def makeImage(w = 40, h = 30, roadTop = None, roadBox = None):
    img = Image.new('RGB', (w, h), BACKGROUND)
    if roadTop is not None:
        roadBox = (0, roadTop, w, h)
    if roadBox is not None:
        x0, y0, x1, y1 = roadBox
        for x in range(x0, x1):
            for y in range(y0, y1):
                img.putpixel((x, y), ROAD)
    return img


def test_analyze_regions_matches_single_bfs():
    img = makeImage(roadTop=20)                 # 40x10 = 400 px 的道路區塊
    regions, floorRegion = marking.analyzeRegions(img)
    assert len(regions) == 1
    assert regions[0][2] == 400
    assert floorRegion == marking.calcCenterPos(img, (img.size[0] // 2, img.size[1] - 1))
    assert floorRegion == (regions[0][1], regions[0][2])


def test_judge_floor_same_with_and_without_precomputed_region():
    img = makeImage(roadTop=20)
    _, floorRegion = marking.analyzeRegions(img)
    assert marking.judgeFloor(img, floorRegion) is True
    assert marking.judgeFloor(img) is True      # 舊呼叫方式結果一致


def test_not_on_road_when_bottom_center_is_background():
    img = makeImage()                           # 整張都不是道路色
    regions, floorRegion = marking.analyzeRegions(img)
    assert regions == []
    assert floorRegion is None
    assert marking.judgeFloor(img, floorRegion) is False
    assert marking.judgeFloor(img) is False


def test_area_below_threshold_is_not_walkable():
    img = makeImage(roadBox=(15, 20, 25, 30))   # 10x10 = 100 px < 300 px 門檻
    regions, floorRegion = marking.analyzeRegions(img)
    assert floorRegion[1] == 100
    assert marking.judgeFloor(img, floorRegion) is False
    marking.drawCenter(img, regions)            # 未達門檻不畫重心圓
    assert img.getpixel(floorRegion[0]) == ROAD


def test_draw_center_marks_region_above_threshold():
    img = makeImage(roadTop=20)
    regions, _ = marking.analyzeRegions(img)
    marking.drawCenter(img, regions)
    assert img.getpixel(regions[0][1]) == marking.centerColors[0]


def test_two_regions_are_counted_separately():
    img = makeImage(w=60, roadBox=(0, 20, 20, 30))
    for x in range(40, 60):                     # 右側另一塊不相連的道路
        for y in range(20, 30):
            img.putpixel((x, y), ROAD)
    regions, floorRegion = marking.analyzeRegions(img)
    assert sorted(area for _, _, area in regions) == [200, 200]
    assert floorRegion is None                  # 底部中央落在中間的背景區
