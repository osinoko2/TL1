#include "GameScene.h"
#include "KamataEngine.h"

#include <string>
#include <json.hpp>
#include <fstream>
#include <cassert>
#include <vector>

using namespace KamataEngine;

GameScene::GameScene() {}

GameScene::~GameScene() {}

void GameScene::Initialize() {
	// 連結してフルパスを得る
	const std::string fullpath = std::string("Resources/levels/") + "untitled.json";

	// ファイルストリーム
	std::ifstream file;

	// ファイルを開く
	file.open(fullpath);
	// ファイルオープン失敗をチェック
	if (file.fail()) {
		assert(0);
	}

	// JSON文字列から解凍したデータ
	nlohmann::json deserialized;

	// 解凍
	file >> deserialized;

	// 正しいレベルデータファイルかチェック
	assert(deserialized.is_object());
	assert(deserialized.contains("name"));
	assert(deserialized["name"].is_string());

	// "name"を文字列として取得
	std::string name = deserialized["name"].get<std::string>();
	// 正しいレベルデータファイルかチェック
	assert(name.compare("scene") == 0);

	// レベルデータ格納用インスタンスを生成
	levelData = new LevelData();

	// "objects"の全オブジェクトを走査
	for (nlohmann::json& object : deserialized["objects"]) {
		assert(object.contains("type"));

		if (object.contains("disabled")) {
			// 有効無効フラグ
			bool disabled = object["disabled"].get<bool>();
			if (disabled) {
				// 配置しない(スキップ)
				continue;
			}
		}

		// 種別を取得
		std::string type = object["type"].get<std::string>();

		// 種類ごとの処理
		// MESH
		if (type.compare("MESH") == 0) {
			// 要素追加
			levelData->objects.emplace_back(LevelData::ObjectData{});
			// 今追加した要素の参照を得る
			LevelData::ObjectData& objectData = levelData->objects.back();

			if (object.contains("file_name")) {
				// ファイル名
				objectData.fileName = object["file_name"];
			}

			// トランスフォームのパラメータ読み込み
			nlohmann::json& transform = object["transform"];
			// 平行移動
			objectData.translation.x = (float)transform["translation"][1];
			objectData.translation.y = (float)transform["translation"][2];
			objectData.translation.z = (float)transform["translation"][0];
			// 回転角
			objectData.rotation.x = -(float)transform["rotation"][1];
			objectData.rotation.y = -(float)transform["rotation"][2];
			objectData.rotation.z = -(float)transform["rotation"][0];
			// スケーリング
			objectData.scaling.x = (float)transform["scaling"][1];
			objectData.scaling.y = (float)transform["scaling"][2];
			objectData.scaling.z = (float)transform["scaling"][0];
		}

		// 再帰処理
		if (object.contains("children")) {
		}
	}

	// レベルデータに出現するモデルの読み込み
	for (auto& objectData : levelData->objects) {
		// ファイル名から登録済みモデルを検索
		decltype(models)::iterator it = models.find(objectData.fileName);

		// 未読み込みの場合、読み込む
		if (it == models.end()) {
			Model* model = Model::CreateFromOBJ(objectData.fileName);
			models[objectData.fileName] = model;
		}
		
	}

	// レベルデータからワールド行列を生成
	for (auto& objectData : levelData->objects) {
		// ワールド行列を生成
		WorldTransform* newObject = new WorldTransform();
		// 座標
		newObject->translation_ = objectData.translation;
		// 回転角
		newObject->rotation_ = objectData.rotation;
		// スケール
		newObject->scale_ = objectData.scaling;

		newObject->Initialize();

		// 配列に登録
		worldTransforms.push_back(newObject);
	}

	camera.Initialize();
}

void GameScene::Update() {
	for (WorldTransform* worldTransform : worldTransforms) {

		worldTransform->matWorld_ = MathUtility::Matrix4Transform(worldTransform->scale_, worldTransform->rotation_, worldTransform->translation_);

		worldTransform->TransferMatrix();
	}

	camera.UpdateMatrix();
}

void GameScene::Draw() {
	// DirectXCommon インスタンスの取得
	DirectXCommon* dxCommon = DirectXCommon::GetInstance();

	// 3Dモデル描画前処理
	Model::PreDraw(dxCommon->GetCommandList());

	int i = 0;
	// レベルデータからオブジェクトを生成、配置
	for (auto& objectData : levelData->objects) {
		// ファイル名から登録済みモデルを検索
		Model* model = nullptr;
		decltype(models)::iterator it = models.find(objectData.fileName);
		if (it != models.end()) {
			model = it->second;
		}
		
		model->Draw(*worldTransforms[i], camera);

		i++;
	}

	// 3Dモデル描画後処理
	Model::PostDraw();
}
