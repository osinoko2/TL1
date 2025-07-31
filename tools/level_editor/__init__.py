import gpu
import gpu_extras.batch
import bpy
import mathutils
import copy

# モジュールのインポート
from .stretch_vertex import MYADDON_OT_stretch_vertex
from .create_ico_sphere import MYADDON_OT_create_ico_sphere
from .export_scene import MYADDON_OT_export_scene
from .my_menu import TOPBAR_MT_my_menu
from .file_name import OBJECT_PT_file_name
from .add_filename import MYADDON_OT_add_filename
from .add_collider import MYADDON_OT_add_collider
from .Collider import OBJECT_PT_collider
from .disabled import MYADDON_OT_add_disabled
from .disabled import OBJECT_PT_disabled

#ブレンダーに登録するアドオン情報
bl_info = {
    "name": "11_レベルエディタ",
    "author": "Shosei Sakurai",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "",
    "description": "レベルエディタ",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

# メニュー項目描画
def draw_menu_manual(self, context):
    #self : 呼び出し元のクラスインスタンス。C++でいうthisポインタ
    #context : カーソルを合わせた時のポップアップのカスタマイズ等に使用

    #トップバーの「エディターメニュー」に項目(オペレータ)を追加
    self.layout.operator("wm.url_open_preset", text="Manual", icon="HELP")

#コライダー描画
class DrawCollider:

    # 描画ハンドル
    handle = None

    #3Dビューに登録する描画関数
    def draw_collider():
        #頂点データ
        vertices = {"pos":[]}
        #インデックスデータ
        indices = []

        #各頂点の、オブジェクト中心からのオフセット
        offsets = [
            [-0.5, -0.5, -0.5], #左下前
            [+0.5, -0.5, -0.5], #右下前
            [-0.5, +0.5, -0.5], #左上前
            [+0.5, +0.5, -0.5], #右上前
            [-0.5, -0.5, +0.5], #左下奥
            [+0.5, -0.5, +0.5], #右下奥
            [-0.5, +0.5, +0.5], #左上奥
            [+0.5, +0.5, +0.5], #右上奥
        ]

        #立方体のX,Y,Z方向サイズ
        size = [2, 2, 2]

        #現在シーンのオブジェクトリストを走査
        for object in bpy.context.scene.objects:

            #コライダープロパティがなければ、描画をスキップ
            if not "collider" in object:
                continue
            
            #中心点、サイズの変数を宣言
            center = mathutils.Vector((0,0,0))
            size = mathutils.Vector((2,2,2))

            #プロパティから値を取得
            center[0]=object["collider_center"][0]
            center[1]=object["collider_center"][1]
            center[2]=object["collider_center"][2]
            size[0]=object["collider_size"][0]
            size[1]=object["collider_size"][1]
            size[2]=object["collider_size"][2]

            #追加前の頂点数
            start = len(vertices["pos"])

            #Boxの8頂点分回す
            for offset in offsets:
                #オブジェクトの中心座標をコピー
                pos = copy.copy(center)
                #中心点を基準に各頂点ごとにずらす
                pos[0]+=offset[0]*size[0]
                pos[1]+=offset[1]*size[1]
                pos[2]+=offset[2]*size[2]
                #ローカル座標からワールド座標に変換
                pos = object.matrix_world @ pos
                #頂点データリストに座標を追加
                vertices['pos'].append(pos)
                #前面を構成する辺の頂点インデックス
                indices.append([start+0,start+1])
                indices.append([start+2,start+3])
                indices.append([start+0,start+2])
                indices.append([start+1,start+3])
                #奥面を構成する辺の頂点インデックス
                indices.append([start+4,start+5])
                indices.append([start+6,start+7])
                indices.append([start+4,start+6])
                indices.append([start+5,start+7])
                #前と頂点を繋ぐ辺の頂点インデックス
                indices.append([start+0,start+4])
                indices.append([start+1,start+5])
                indices.append([start+2,start+6])
                indices.append([start+3,start+7])

        #ビルトインのシェーダを取得
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        #バッチを作成(引数 : シェーダ、トポロジー、頂点データ、インデックスデータ)
        batch = gpu_extras.batch.batch_for_shader(shader, "LINES", vertices, indices = indices)

        #シェーダのパラメータ設定
        color = [0.5, 1.0, 1.0, 1.0]
        shader.bind()
        shader.uniform_float("color", color)
        #描画
        batch.draw(shader)


#Blenderに登録するクラスリスト
classes = (
    MYADDON_OT_export_scene,
    MYADDON_OT_create_ico_sphere,
    MYADDON_OT_stretch_vertex,
    MYADDON_OT_add_filename,
    MYADDON_OT_add_collider,
    MYADDON_OT_add_disabled,
    TOPBAR_MT_my_menu,
    OBJECT_PT_file_name,
    OBJECT_PT_collider,
    OBJECT_PT_disabled,
)

#アドオン有効時コールバック
def register():
    #Blenderにクラスを登録
    for cls in classes:
        bpy.utils.register_class(cls)

    #メニューに項目を追加
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_my_menu.submenu)
    #3Dビューに描画関数を追加
    DrawCollider.handle = bpy.types.SpaceView3D.draw_handler_add(DrawCollider.draw_collider, (), "WINDOW", "POST_VIEW")
    print("レベルエディタが有効化されました。")

#アドオン無効時コールバック
def unregister():
    #メニューから項目を削除
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_my_menu.submenu)
    #3Dビューから描画関数を削除
    bpy.types.SpaceView3D.draw_handler_remove(DrawCollider.handle, "WINDOW")

    #Blenderからクラスを削除
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("レベルエディタが無効化されました。")