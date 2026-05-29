#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"

const char* ssid     = "Junction";
const char* password = "h@ck@thon@2026";

#define PWDN_GPIO_NUM    32
#define RESET_GPIO_NUM   -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM    26
#define SIOC_GPIO_NUM    27
#define Y9_GPIO_NUM      35
#define Y8_GPIO_NUM      34
#define Y7_GPIO_NUM      39
#define Y6_GPIO_NUM      36
#define Y5_GPIO_NUM      21
#define Y4_GPIO_NUM      19
#define Y3_GPIO_NUM      18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM   25
#define HREF_GPIO_NUM    23
#define PCLK_GPIO_NUM    22

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

httpd_handle_t camera_httpd = NULL;
httpd_handle_t stream_httpd = NULL;

// ── HTML page served at http://192.168.101.124/ ──────────────────
static const char* html_page = R"rawhtml(
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ESP32-CAM QR Scanner</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, sans-serif; background: #f5f5f0; padding: 16px; color: #1a1a1a; }
h1 { font-size: 17px; font-weight: 500; margin-bottom: 14px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media(max-width:520px){ .grid { grid-template-columns: 1fr; } }
.card { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; }
.card-head { padding: 9px 13px; font-size: 13px; font-weight: 500; border-bottom: 1px solid #f0f0f0; background: #fafafa; }
#streamImg { width: 100%; display: block; background: #111; min-height: 180px; }
canvas { display: none; }
.body { padding: 13px; }
.lbl { font-size: 11px; color: #999; margin-bottom: 5px; letter-spacing: 0.4px; }
.result { font-family: monospace; font-size: 13px; background: #f5f5f0; border-radius: 7px; padding: 9px 11px; min-height: 44px; word-break: break-all; border-left: 3px solid #e0e0e0; transition: border-color 0.3s, background 0.3s; }
.result.hit { border-left-color: #1D9E75; background: #f0faf6; }
.btns { display: flex; gap: 7px; margin-top: 9px; flex-wrap: wrap; }
button { padding: 6px 13px; border: 1px solid #ccc; border-radius: 7px; font-size: 12px; background: #fff; cursor: pointer; }
button:hover { background: #f0f0f0; }
.stats { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin-top: 9px; }
.stat { background: #f5f5f0; border-radius: 7px; padding: 7px 10px; }
.stat-n { font-size: 20px; font-weight: 500; }
.stat-l { font-size: 11px; color: #999; }
.history { max-height: 160px; overflow-y: auto; }
.hi { display: flex; gap: 9px; padding: 6px 13px; border-bottom: 1px solid #f5f5f0; font-size: 12px; }
.hi:last-child { border-bottom: none; }
.hi-t { color: #bbb; font-family: monospace; flex-shrink: 0; }
.hi-v { font-family: monospace; word-break: break-all; }
.empty { font-size: 13px; color: #bbb; text-align: center; padding: 18px; }
.flash { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(29,158,117,0.15); pointer-events: none; opacity: 0; transition: opacity 0.15s; z-index: 99; }
.flash.show { opacity: 1; }
.status { font-size: 12px; color: #1D9E75; margin-bottom: 10px; }
</style>
</head>
<body>
<h1>ESP32-CAM QR Scanner</h1>
<p class="status" id="status">● Connecting to stream...</p>

<div class="grid" style="margin-bottom:12px;">
  <div class="card">
    <div class="card-head">Live stream</div>
    <img id="streamImg" src="/stream" alt="stream" crossorigin="anonymous" />
    <canvas id="canvas"></canvas>
  </div>
  <div class="card">
    <div class="card-head">QR decode</div>
    <div class="body">
      <div class="lbl">Last decoded value</div>
      <div class="result" id="result">Waiting for QR code...</div>
      <div class="btns">
        <button onclick="copyVal()">Copy</button>
        <button onclick="openVal()">Open URL</button>
        <button onclick="clearAll()">Clear</button>
      </div>
      <div class="stats">
        <div class="stat"><div class="stat-n" id="scanCount">0</div><div class="stat-l">total scans</div></div>
        <div class="stat"><div class="stat-n" id="fps">0</div><div class="stat-l">decode/sec</div></div>
      </div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-head">Scan history</div>
  <div class="history" id="history"><div class="empty">No scans yet</div></div>
</div>

<div class="flash" id="flash"></div>

<script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js"></script>
<script>
const img = document.getElementById('streamImg');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d', { willReadFrequently: true });
let history = [], scanCount = 0, lastVal = '', frameHits = 0;

img.onload = () => document.getElementById('status').textContent = '● Streaming';
img.onerror = () => document.getElementById('status').textContent = '✕ Stream error — refresh page';

setInterval(() => {
  document.getElementById('fps').textContent = frameHits;
  frameHits = 0;
}, 1000);

function decode() {
  if (img.naturalWidth > 0) {
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    ctx.drawImage(img, 0, 0);
    const d = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const code = jsQR(d.data, d.width, d.height, { inversionAttempts: 'dontInvert' });
    if (code && code.data && code.data !== lastVal) {
      lastVal = code.data;
      scanCount++;
      frameHits++;
      document.getElementById('scanCount').textContent = scanCount;
      const r = document.getElementById('result');
      r.textContent = code.data;
      r.className = 'result hit';
      setTimeout(() => r.className = 'result', 3000);
      const f = document.getElementById('flash');
      f.classList.add('show');
      setTimeout(() => f.classList.remove('show'), 200);
      history.unshift({ t: new Date().toTimeString().slice(0,8), v: code.data });
      if (history.length > 100) history.pop();
      renderHistory();
    }
  }
  requestAnimationFrame(decode);
}
decode();

function renderHistory() {
  document.getElementById('history').innerHTML = history.length
    ? history.map(h => `<div class="hi"><span class="hi-t">${h.t}</span><span class="hi-v">${h.v.replace(/</g,'&lt;')}</span></div>`).join('')
    : '<div class="empty">No scans yet</div>';
}
function copyVal() {
  const v = document.getElementById('result').textContent;
  if (v && v !== 'Waiting for QR code...') navigator.clipboard.writeText(v);
}
function openVal() {
  const v = document.getElementById('result').textContent;
  if (v.startsWith('http')) window.open(v, '_blank'); else alert('Not a URL');
}
function clearAll() {
  history = []; lastVal = ''; scanCount = 0;
  document.getElementById('scanCount').textContent = '0';
  document.getElementById('result').textContent = 'Waiting for QR code...';
  renderHistory();
}
</script>
</body>
</html>
)rawhtml";

// ── HTML handler ──────────────────────────────────────────────────
static esp_err_t index_handler(httpd_req_t *req) {
  httpd_resp_set_type(req, "text/html");
  httpd_resp_send(req, html_page, strlen(html_page));
  return ESP_OK;
}

// ── Stream handler ────────────────────────────────────────────────
static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t* fb = NULL;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t* _jpg_buf = NULL;
  char part_buf[64];

  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if (res != ESP_OK) return res;

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) { res = ESP_FAIL; break; }

    if (fb->format != PIXFORMAT_JPEG) {
      bool ok = frame2jpg(fb, 12, &_jpg_buf, &_jpg_buf_len);
      esp_camera_fb_return(fb); fb = NULL;
      if (!ok) { res = ESP_FAIL; break; }
    } else {
      _jpg_buf_len = fb->len;
      _jpg_buf = fb->buf;
    }

    res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
    if (res == ESP_OK) {
      size_t hlen = snprintf(part_buf, 64, _STREAM_PART, _jpg_buf_len);
      res = httpd_resp_send_chunk(req, part_buf, hlen);
    }
    if (res == ESP_OK)
      res = httpd_resp_send_chunk(req, (const char*)_jpg_buf, _jpg_buf_len);

    if (fb) { esp_camera_fb_return(fb); fb = NULL; }
    else free(_jpg_buf);

    if (res != ESP_OK) break;
  }
  return res;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM; config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM; config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM; config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM; config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size   = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count     = 1;

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init FAILED"); return;
  }

  sensor_t* s = esp_camera_sensor_get();
  s->set_whitebal(s, 1);
  s->set_awb_gain(s, 1);
  s->set_exposure_ctrl(s, 1);
  s->set_gain_ctrl(s, 1);
  s->set_contrast(s, 1);
  s->set_sharpness(s, 1);

  WiFi.begin(ssid, password);
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi connected!");
  Serial.println("Open this in browser: http://" + WiFi.localIP().toString());

  // server on port 80 — serves HTML + stream
  httpd_config_t cfg = HTTPD_DEFAULT_CONFIG();
  cfg.server_port = 80;
  cfg.max_uri_handlers = 4;

  httpd_uri_t index_uri = { "/",       HTTP_GET, index_handler, NULL };
  httpd_uri_t stream_uri = { "/stream", HTTP_GET, stream_handler, NULL };

  if (httpd_start(&camera_httpd, &cfg) == ESP_OK) {
    httpd_register_uri_handler(camera_httpd, &index_uri);
    httpd_register_uri_handler(camera_httpd, &stream_uri);
  }
}

void loop() { delay(1); }
