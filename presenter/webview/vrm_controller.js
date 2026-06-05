/**
 * VRM 角色控制器
 * 负责 3D 角色的动画、表情、口型同步
 * 通过 window.vrmController 暴露给 HTML 和 Python 调用
 */

class VRMController {
    constructor() {
        this.vrm = null;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.clock = new THREE.Clock();
        this.mixer = null;
        this.character = null;

        this._blinkTimer = 0;
        this._idleTime = 0;
        this._bubbleTimer = null;

        this._init();
    }

    async _init() {
        this._initScene();
        this._initLights();
        await this._loadModel();
        this._animate();
        this._setupResize();

        document.getElementById('loading').style.display = 'none';
        console.log('[VRM] 控制器就绪');
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
    }

    async _loadModel() {
        try {
            const response = await fetch('./models/default.vrm');
            if (!response.ok) throw new Error('未找到模型文件');
            const gltf = await response.arrayBuffer();
            // TODO: 使用 @pixiv/three-vrm 加载 VRM 模型
            this._createPlaceholder();
        } catch (e) {
            console.log('[VRM] 未找到 VRM 模型，使用占位角色:', e.message);
            this._createPlaceholder();
        }
    }

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
        const hair = new THREE.Mesh(
            new THREE.SphereGeometry(0.3, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2),
            new THREE.MeshStandardMaterial({ color: 0x443366 })
        );
        hair.position.y = 0.78;
        group.add(hair);

        this.character = group;
        this.scene.add(group);
    }

    _animate() {
        requestAnimationFrame(() => this._animate());
        const delta = this.clock.getDelta();

        if (this.character) {
            this._idleTime += delta;
            this.character.position.y = Math.sin(this._idleTime * 1.5) * 0.003;

            this._blinkTimer += delta;
            if (this._blinkTimer > 3 + Math.random() * 4) {
                this._blink();
                this._blinkTimer = 0;
            }
        }

        this.renderer.render(this.scene, this.camera);
    }

    _blink() {
        if (!this._eyeL || !this._eyeR) return;
        this._eyeL.scale.y = 0.1;
        this._eyeR.scale.y = 0.1;
        setTimeout(() => {
            if (this._eyeL) this._eyeL.scale.y = 1;
            if (this._eyeR) this._eyeR.scale.y = 1;
        }, 150);
    }

    _setupResize() {
        window.addEventListener('resize', () => {
            const container = document.getElementById('canvas-container');
            const w = container.clientWidth;
            const h = container.clientHeight;
            this.camera.aspect = w / h;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(w, h);
        });
    }

    // ======== 外部调用接口 ========

    speak(text, expression = 'neutral') {
        const bubble = document.getElementById('bubble');
        if (!bubble) return;
        bubble.textContent = text;
        bubble.style.display = 'block';
        clearTimeout(this._bubbleTimer);
        this._bubbleTimer = setTimeout(() => {
            bubble.style.display = 'none';
        }, Math.max(2000, text.length * 150));

        // 口型动一下
        if (this._mouth) {
            this._mouth.scale.y = 0.8;
            setTimeout(() => { if (this._mouth) this._mouth.scale.y = 0.4; }, 200);
        }
    }

    showThinking() {
        const el = document.getElementById('thinking');
        if (el) el.style.display = 'block';
    }

    hideThinking() {
        const el = document.getElementById('thinking');
        if (el) el.style.display = 'none';
    }

    setExpression(expr) {
        // 表情控制接口（VRM模型扩展）
    }

    playIdle(action) {
        if (!this.character) return;
        switch (action) {
            case 'blink': this._blink(); break;
            case 'tilt':
                this.character.rotation.z = 0.05;
                setTimeout(() => { if (this.character) this.character.rotation.z = 0; }, 500);
                break;
            case 'look_around':
                if (this._head) {
                    this._head.rotation.y = 0.2;
                    setTimeout(() => { if (this._head) this._head.rotation.y = 0; }, 800);
                }
                break;
        }
    }
}

// 注册到全局
window.vrmController = new VRMController();
