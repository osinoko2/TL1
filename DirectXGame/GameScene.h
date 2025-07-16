#pragma once
#include "KamataEngine.h"
#include <map>
#include <string>

class GameScene {
	// レベルデータ
	struct LevelData {
		// オブジェクト1個分のデータ
		struct ObjectData {
			std::string fileName;
			KamataEngine::Vector3 translation;
			KamataEngine::Vector3 rotation;
			KamataEngine::Vector3 scaling;
		};

		// オブジェクトのコンテナ
		std::vector<ObjectData> objects;
	};

public:
	// コンストラクタ
	GameScene();

	// デストラクタ
	~GameScene();

	// 初期化
	void Initialize();

	// 更新
	void Update();

	// 描画
	void Draw();

private:
	// レベルデータ格納用インスタンスを生成
	LevelData* levelData = nullptr;

	// オブジェクトデータ
	std::vector<KamataEngine::WorldTransform*> worldTransforms;

	std::map<std::string, KamataEngine::Model*> models;

	KamataEngine::Camera camera;
};
