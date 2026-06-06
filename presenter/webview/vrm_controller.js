/**
 * VRM 角色控制器 - ES Module
 * ============================
 * 桌面伴侣 3D 角色控制器，支持 VRM 1.0 模型加载、动画、表情、口型同步。
 *
 * 使用方式 (在 HTML 中):
 * ```html
 * <script type="importmap">
 * {
 *   "imports": {
 *     "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
 *     "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
 *   }
 * }
 * </script>
 * <script type="module">
 *   import { VRMController } from './vrm_controller.js';
 *   window.vrmController = new VRMController();
 * </script>
 * ```
 *
 * 依赖:
 *   - three.js (CDN, 见 importmap)
 *   - @pixiv/three-vrm@3.1.0 (动态加载，CDN 不可用时优雅降级为占位角色)
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export class VRMController {
  constructor() {
    // Three.js 核心
    this.vrm = null;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.clock = new THREE.Clock();

    // 占位角色引用
    this.character = null;
    this._head = null;
    this._eyeL = null;
    this._eyeR = null;
    this._mouth = null;

    // VRM 状态
    this._vrmLoaded = false;

    // 动画状态
    this._blinkTimer = 0;
    this._idleTime = 0;
    this._bubbleTimer = null;
    this._isSpeaking = false;
    this._lipSyncTimer = 0;
    this._currentExpression = 'neutral';
    this._lipSyncTimeout = null;

    // 自启动
    this._init();
  }

  // ======================== 初始化 ========================

  async _init() {
    this._initScene();
    this._initLights();
    await this._loadVRM();
    this._animate();
    this._setupResize();
  }

  _initScene() {
    this.scene = new THREE.Scene();
    this.scene.background = null;

    const container = document.getElementById('canvas-container');
    const w = container.clientWidth;
    const h = container.clientHeight;

    this.camera = new THREE.PerspectiveCamera(35, w / h, 0.1, 20);
    this.camera.position.set(0, 1.2, -2.5);
    this.camera.lookAt(0, 1.0, 0);

    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      preserveDrawingBuffer: true
    });
    this.renderer.setSize(w, h);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.0;
    container.appendChild(this.renderer.domElement);
  }

  _initLights() {
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.6));

    const main = new THREE.DirectionalLight(0xffffff, 1.2);
    main.position.set(1, 2, 2);
    this.scene.add(main);

    const fill = new THREE.DirectionalLight(0x8888ff, 0.4);
    fill.position.set(-1, 1, 1);
    this.scene.add(fill);

    const rim = new THREE.DirectionalLight(0xffffff, 0.5);
    rim.position.set(0, 1, -2);
    this.scene.add(rim);
  }

  // ======================== VRM 模型加载 ========================

  async _loadVRM() {
    try {
      // 动态加载 @pixiv/three-vrm（CDN 不可用时降级）
      let VRMLoaderPlugin;
      try {
        const vrmModule = await import('./lib/three-vrm.module.js');
        VRMLoaderPlugin = vrmModule.VRMLoaderPlugin;
      } catch (localErr) {
        console.warn('[VRM] VRM 模块加载失败:', localErr.message);
        throw new Error('VRM 依赖不可用');
      }

      const loader = new GLTFLoader();
      loader.registerPlugin(new VRMLoaderPlugin());

      const gltf = await loader.loadAsync('./models/default.vrm');

      if (!gltf.userData.vrm) {
        throw new Error('模型中未找到 VRM 数据');
      }

      this.vrm = gltf.userData.vrm;
      this.vrm.scene.position.set(0, 0, 0);
      this.scene.add(this.vrm.scene);

      this._vrmLoaded = true;

      // 注视追踪
      if (this.vrm.lookAt && typeof this.vrm.lookAt.target !== 'undefined') {
        this.vrm.lookAt.target = this.camera;
      }

      // 适配 VRM 灯光
      this._setupVRMLighting();

      document.getElementById('loading').style.display = 'none';
      console.log('[VRM] 模型加载成功');
    } catch (e) {
      console.warn('[VRM] VRM 加载失败，使用占位角色:', e.message);
      this._createPlaceholder();
      document.getElementById('loading').style.display = 'none';
    }
  }

  _setupVRMLighting() {
    const ambient = this.scene.children.find(c => c instanceof THREE.AmbientLight);
    if (ambient) ambient.intensity = 0.7;

    const dirLights = this.scene.children.filter(c => c instanceof THREE.DirectionalLight);
    if (dirLights.length > 0) {
      dirLights[0].intensity = 1.4;
    }
  }

  // ======================== 占位角色（回退方案） ========================

  _createPlaceholder() {
    const group = new THREE.Group();

    // 身体
    const body = new THREE.Mesh(
      new THREE.CylinderGeometry(0.3, 0.35, 0.6, 12),
      new THREE.MeshStandardMaterial({ color: 0xF5A0B0, roughness: 0.3 })
    );
    body.position.y = 0.3;
    group.add(body);

    // 头部
    this._head = new THREE.Mesh(
      new THREE.SphereGeometry(0.28, 16, 16),
      new THREE.MeshStandardMaterial({ color: 0xFFE0C0, roughness: 0.2 })
    );
    this._head.position.y = 0.75;
    group.add(this._head);

    // 眼睛
    const eyeMat = new THREE.MeshStandardMaterial({ color: 0x333333 });
    const eyeGeo = new THREE.SphereGeometry(0.05, 8, 8);
    this._eyeL = new THREE.Mesh(eyeGeo, eyeMat);
    this._eyeL.position.set(-0.1, 0.8, 0.25);
    group.add(this._eyeL);
    this._eyeR = new THREE.Mesh(eyeGeo, eyeMat);
    this._eyeR.position.set(0.1, 0.8, 0.25);
    group.add(this._eyeR);

    // 嘴巴
    this._mouth = new THREE.Mesh(
      new THREE.SphereGeometry(0.03, 8, 8),
      new THREE.MeshStandardMaterial({ color: 0xDD6688 })
    );
    this._mouth.position.set(0, 0.68, 0.28);
    this._mouth.scale.set(1, 0.4, 0.5);
    group.add(this._mouth);

    // 头发
    const hairMat = new THREE.MeshStandardMaterial({ color: 0x443366 });
    const hair = new THREE.Mesh(
      new THREE.SphereGeometry(0.3, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2),
      hairMat
    );
    hair.position.y = 0.78;
    group.add(hair);

    // 手臂
    const armMat = new THREE.MeshStandardMaterial({ color: 0xFFE0C0 });
    const armGeo = new THREE.CylinderGeometry(0.04, 0.05, 0.3, 8);
    const armL = new THREE.Mesh(armGeo, armMat);
    armL.position.set(-0.35, 0.5, 0);
    armL.rotation.z = 0.2;
    group.add(armL);
    const armR = new THREE.Mesh(armGeo, armMat);
    armR.position.set(0.35, 0.5, 0);
    armR.rotation.z = -0.2;
    group.add(armR);

    this.character = group;
    this.scene.add(group);
  }

  // ======================== 动画循环 ========================

  _animate() {
    requestAnimationFrame(() => this._animate());
    const delta = Math.min(this.clock.getDelta(), 0.05);

    if (this._vrmLoaded && this.vrm) {
      this._updateVRM(delta);
    } else if (this.character) {
      this._updatePlaceholder(delta);
    }

    this.renderer.render(this.scene, this.camera);
  }

  _updateVRM(delta) {
    this._idleTime += delta;

    if (typeof this.vrm.update === 'function') {
      this.vrm.update(delta);
    }

    // 呼吸
    const breath = Math.sin(this._idleTime * 1.2) * 0.002;
    this.vrm.scene.position.y = breath;

    // 头部微晃
    if (this.vrm.humanoid) {
      const headNode = this.vrm.humanoid.getRawBoneNode('head');
      if (headNode) {
        headNode.rotation.x += Math.sin(this._idleTime * 0.5) * 0.0005;
        headNode.rotation.z += Math.cos(this._idleTime * 0.3) * 0.0003;
      }
    }

    // 眨眼
    this._blinkTimer += delta;
    if (this._blinkTimer > 2.5 + Math.random() * 4) {
      this._vrmBlink();
      this._blinkTimer = 0;
    }

    // 口型同步
    if (this._isSpeaking) {
      this._updateLipSync(delta);
    }

    // 注视更新
    if (this.vrm.lookAt && typeof this.vrm.lookAt.update === 'function') {
      this.vrm.lookAt.update(delta);
    }

    // 表情/BlendShape 刷新（兼容 VRM 1.0 和 0.x）
    const api = this._getBlendAPI();
    if (api && typeof api.update === 'function') {
      api.update();
    }
  }

  _updatePlaceholder(delta) {
    this._idleTime += delta;

    this.character.position.y = Math.sin(this._idleTime * 1.5) * 0.003;

    if (this._head) {
      this._head.rotation.x = Math.sin(this._idleTime * 0.5) * 0.03;
      this._head.rotation.z = Math.cos(this._idleTime * 0.3) * 0.02;
    }

    this._blinkTimer += delta;
    if (this._blinkTimer > 3 + Math.random() * 4) {
      this._blink();
      this._blinkTimer = 0;
    }

    if (this._isSpeaking && this._mouth) {
      const mouthOpen = 0.6 + Math.sin(this._idleTime * 15) * 0.3;
      this._mouth.scale.y = Math.max(0.1, mouthOpen);
    } else if (this._mouth) {
      this._mouth.scale.y = 0.4;
    }
  }

  // ======================== 眨眼 ========================

  _blink() {
    if (!this._eyeL || !this._eyeR) return;
    this._eyeL.scale.y = 0.1;
    this._eyeR.scale.y = 0.1;
    setTimeout(() => {
      if (this._eyeL) this._eyeL.scale.y = 1;
      if (this._eyeR) this._eyeR.scale.y = 1;
    }, 120);
  }

  _getBlendAPI() {
    // 兼容 VRM 1.0 (expressionManager) 和 VRM 0.x (blendShapeProxy)
    if (this.vrm) {
      return this.vrm.expressionManager || this.vrm.blendShapeProxy || null;
    }
    return null;
  }

  _vrmBlink() {
    const api = this._getBlendAPI();
    if (!api) return;
    try {
      api.setValue('blink', 1.0);
      api.setValue('Blink', 1.0);
      if (typeof api.update === 'function') api.update();
      setTimeout(() => {
        if (api) {
          api.setValue('blink', 0.0);
          api.setValue('Blink', 0.0);
          if (typeof api.update === 'function') api.update();
        }
      }, 100);
    } catch (e) { /* 静默 */ }
  }

  // ======================== 口型同步 ========================

  _startLipSync() {
    this._isSpeaking = true;
    this._lipSyncTimer = 0;
  }

  _stopLipSync() {
    this._isSpeaking = false;
    const api = this._getBlendAPI();
    if (api) {
      try {
        const vrm1Shapes = ['aa', 'ih', 'ou', 'ee', 'oh'];
        const vrm0Shapes = ['A', 'I', 'U', 'E', 'O'];
        [...vrm1Shapes, ...vrm0Shapes].forEach(s => api.setValue(s, 0));
        if (typeof api.update === 'function') api.update();
      } catch (e) { /* 静默 */ }
    }
  }

  _updateLipSync(delta) {
    this._lipSyncTimer += delta;
    if (this._lipSyncTimer < 0.08) return;
    this._lipSyncTimer = 0;

    const api = this._getBlendAPI();
    if (!api) return;

    try {
      const vrm1Shapes = ['aa', 'ih', 'ou', 'ee', 'oh'];
      const vrm0Shapes = ['A', 'I', 'U', 'E', 'O'];
      [...vrm1Shapes, ...vrm0Shapes].forEach(s => api.setValue(s, 0));

      const useVrm1 = !!this.vrm.expressionManager;
      const shapes = useVrm1 ? vrm1Shapes : vrm0Shapes;
      const shape = shapes[Math.floor(Math.random() * shapes.length)];
      const intensity = 0.5 + Math.random() * 0.5;
      api.setValue(shape, intensity);

      if (typeof api.update === 'function') api.update();
    } catch (e) { /* 静默 */ }
  }

  // ======================== 窗口缩放 ========================

  _setupResize() {
    window.addEventListener('resize', () => {
      const container = document.getElementById('canvas-container');
      const w = container.clientWidth;
      const h = container.clientHeight;
      if (w === 0 || h === 0) return;
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    });
  }

  // ======================== 公开接口 ========================

  /**
   * 角色说话
   * @param {string} text
   * @param {string} expression 'neutral'|'happy'|'sad'|'surprised'|'angry'
   */
  speak(text, expression = 'neutral') {
    const bubble = document.getElementById('bubble');
    if (bubble) {
      bubble.textContent = text;
      bubble.style.display = 'block';
      clearTimeout(this._bubbleTimer);
      this._bubbleTimer = setTimeout(() => {
        bubble.style.display = 'none';
      }, Math.max(2000, text.length * 150));
    }

    this.setExpression(expression);

    this._startLipSync();
    const duration = Math.max(2000, text.length * 150);
    clearTimeout(this._lipSyncTimeout);
    this._lipSyncTimeout = setTimeout(() => {
      this._stopLipSync();
    }, duration);

    console.log('[VRM] 说话:', text);
  }

  /** 显示思考动画 */
  showThinking() {
    const el = document.getElementById('thinking');
    if (el) el.style.display = 'block';
  }

  /** 隐藏思考动画 */
  hideThinking() {
    const el = document.getElementById('thinking');
    if (el) el.style.display = 'none';
  }

  /**
   * 设置表情
   * @param {string} expr neutral|happy|sad|surprised|angry
   */
  setExpression(expr) {
    this._currentExpression = expr;

    const api = this._getBlendAPI();
    if (api) {
      try {
        // 清空之前的表情（兼容 VRM 1.0 和 0.x）
        const vrm1Exprs = ['neutral', 'happy', 'sad', 'surprised', 'angry', 'relaxed'];
        const vrm0Exprs = ['Neutral', 'Happy', 'Sad', 'Surprised', 'Angry', 'Relaxed'];
        [...vrm1Exprs, ...vrm0Exprs].forEach(e => api.setValue(e, 0));

        // 设置新表情
        const target = {
          'neutral': null,
          'happy': 'happy',
          'sad': 'sad',
          'surprised': 'surprised',
          'angry': 'angry'
        }[expr];

        if (target && target !== 'neutral') {
          api.setValue(target, 1.0);
          api.setValue(target.charAt(0).toUpperCase() + target.slice(1), 1.0);
        }
        if (typeof api.update === 'function') api.update();
      } catch (e) { /* 静默 */ }
    }

    console.log('[VRM] 表情:', expr);
  }

  /**
   * 播放闲置动作
   * @param {string} action blink|tilt|look_around|stretch
   */
  playIdle(action) {
    if (this._vrmLoaded && this.vrm) {
      this._playVRMIdle(action);
    } else if (this.character) {
      this._playPlaceholderIdle(action);
    }
  }

  _playVRMIdle(action) {
    switch (action) {
      case 'blink':
        this._vrmBlink();
        break;
      case 'tilt':
        if (this.vrm.humanoid) {
          const head = this.vrm.humanoid.getRawBoneNode('head');
          if (head) {
            head.rotation.z = 0.1;
            setTimeout(() => { if (head) head.rotation.z = 0; }, 400);
          }
        }
        break;
      case 'look_around':
        if (this.vrm.humanoid) {
          const head = this.vrm.humanoid.getRawBoneNode('head');
          if (head) {
            head.rotation.y = 0.3;
            setTimeout(() => { if (head) head.rotation.y = 0; }, 600);
          }
        }
        break;
      case 'stretch':
        if (this.vrm.scene) {
          this.vrm.scene.position.y = 0.01;
          setTimeout(() => {
            if (this.vrm && this.vrm.scene) this.vrm.scene.position.y = 0;
          }, 800);
        }
        break;
    }
  }

  _playPlaceholderIdle(action) {
    switch (action) {
      case 'blink':
        this._blink();
        break;
      case 'tilt':
        if (this.character) {
          this.character.rotation.z = 0.05;
          setTimeout(() => { if (this.character) this.character.rotation.z = 0; }, 400);
        }
        break;
      case 'look_around':
        if (this._head) {
          this._head.rotation.y = 0.2;
          setTimeout(() => { if (this._head) this._head.rotation.y = 0; }, 600);
        }
        break;
      case 'stretch':
        if (this.character) {
          this.character.position.y = 0.008;
          setTimeout(() => { if (this.character) this.character.position.y = 0; }, 800);
        }
        break;
    }
  }
}
