import cv2 as openCV
import numpy as np
import math
from pathlib import Path
from roverlib.plugins.camera.camera import Camera
from roverlib.utils.config_manager import Config
from .lineMemory import memory
from .lineDecision import decision

class LineDetectorApp:
    def __init__(self, config_path: Path):
        self.config = Config(config_path)
        self.height = 640
        self.width = 640
        self.start = False
        self.drive_mode = None
        
        try:
            self.picam = Camera(self.height, self.width, verticalFlip=True)
            self.picam.start()
            print("Câmera iniciada com sucesso.")
        except Exception as e:
            print(f"Erro ao iniciar câmera: {e}")
            self.picam = None

        self.memoria = memory(frames_number=10)
        self.decisao = decision()

    @staticmethod
    def roi_definition(img):
        height, width = img.shape[:2]
        bottom_left = [width * 0.1, height]
        top_left = [width * 0.4, height * 0.6]
        top_right = [width * 0.6, height * 0.6]
        bottom_right = [width * 0.9, height]
        
        poligono = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
        mask = np.zeros_like(img)
        openCV.fillPoly(mask, poligono, 255)
        return openCV.bitwise_and(img, mask)

    @staticmethod
    def extract_coords(lines, drive_mode: str, image_shape):
        left_pts, right_pts, line_pts = [], [], []
        if lines is None or not drive_mode: 
            return None

        for line in lines:
            coords = line.reshape(-1)
            if len(coords) < 4: continue
            x1, y1, x2, y2 = map(int, coords[:4])
            
            dx, dy = x2 - x1, y2 - y1
            abs_angle = abs(math.degrees(math.atan2(dy, dx)))
            
            if 30 > abs_angle or abs_angle > 160: continue
            
            parameters = np.polyfit((x1, x2), (y1, y2), 1)
            slope, intercept = parameters[0], parameters[1]

            if drive_mode == 'road':
                if slope < 0:
                    left_pts.append((slope, intercept))
                else:
                    right_pts.append((slope, intercept))
            else:
                line_pts.append((slope, intercept))

        if drive_mode == 'road':
            left_avg = np.average(left_pts, axis=0) if left_pts else None
            right_avg = np.average(right_pts, axis=0) if right_pts else None
            return left_avg, right_avg
        else:
            return np.average(line_pts, axis=0) if line_pts else None

    @staticmethod
    def cat_x_linepoints(y_min, y_max, line_parameters):
        if line_parameters is None: return None
        slope, intercept = line_parameters
        try:
            x_start = int((y_min - intercept) / slope)
            x_end = int((y_max - intercept) / slope)
            return [[x_start, y_min], [x_end, y_max]]
        except:
            return None

    def lineDetectHough(self, img, isCut=False):
        height, width = img.shape[:2]
        if isCut:
            y_offset = int(height * 0.6)
            workImage = img[y_offset:height, 0:width]
        else:
            y_offset = 0
            workImage = img

        gray = openCV.cvtColor(workImage, openCV.COLOR_BGR2GRAY)
        blur = openCV.GaussianBlur(gray, (5, 5), 0)
        edges = openCV.Canny(blur, 50, 150)
        structElement = openCV.getStructuringElement(openCV.MORPH_RECT, (3, 3))
        edges = openCV.dilate(edges, structElement, iterations=1)
        roi = self.roi_definition(edges)

        lines = openCV.HoughLinesP(roi, rho=2, theta=np.pi/180, threshold=50, minLineLength=40, maxLineGap=175)
        ajustadas = []

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                abs_angle = abs(math.degrees(math.atan2(y2 - y1, x2 - x1)))
                if 30 < abs_angle < 160:
                    ajustadas.append([[x1, y1 + y_offset, x2, y2 + y_offset]])
                    openCV.line(img, (x1, y1 + y_offset), (x2, y2 + y_offset), (0, 255, 0), 2)

        return roi, img, np.array(ajustadas) if ajustadas else None

    def run(self):
        if self.picam is None:
            return
        
        while True:
            frame = self.picam.get_frame()
            if frame is None: continue

            left_avg, right_avg = None, None
            right_point, left_point = None, None
            target_line = None
            result = frame.copy()
            all_points = None
            line_points = None
            direcao, erro = "Aguardando", 0

            roi, frame_linhas, hough_data = self.lineDetectHough(frame)
            y_max = frame.shape[0]
            y_min = int(y_max * 0.6)

            key = openCV.waitKey(10) & 0xFF

            if key == ord('s'):
                self.start = True
                print("Rover iniciado")
            if key == ord('c') and self.start:
                self.drive_mode = None
                self.start = False
                print("Modo resetado")
            if key == ord('r') and self.start:
                self.drive_mode = 'road'
                print("Modo: Road")
            if key == ord('l') and self.start:
                self.drive_mode = 'line'
                print("Modo: Line")

            if self.drive_mode == 'road':
                try:
                    left_avg, right_avg = self.extract_coords(hough_data, self.drive_mode, frame.shape)
                    error_flag = False
                except Exception:
                    error_flag = True
                    result = frame_linhas

                if not error_flag:
                    try:
                        left_avg = self.memoria.suavizar(left_avg, "left")
                        right_avg = self.memoria.suavizar(right_avg, "right")
                        left_point = self.cat_x_linepoints(y_min, y_max, left_avg)
                        right_point = self.cat_x_linepoints(y_min, y_max, right_avg)
                        all_points = (left_point, right_point)
                    except Exception:
                        left_point, right_point = [], []

                    if left_point and right_point:
                        pts = np.array([left_point[0], right_point[0], right_point[1], left_point[1]], np.int32)
                        mask = np.zeros_like(frame)
                        openCV.fillPoly(mask, [pts], (0, 255, 0))
                        result = openCV.addWeighted(frame, 1, mask, 0.4, 0)
                    else:
                        result = frame

            if self.drive_mode == 'line':
                try:
                    line_avg = self.extract_coords(hough_data, self.drive_mode, frame.shape)
                    error_flag = False
                except Exception:
                    error_flag = True

                result = frame_linhas
                if not error_flag:
                    try:
                        line_points = self.cat_x_linepoints(y_min, y_max, line_avg)
                    except Exception:
                        line_points = None

                    if line_points:
                        openCV.line(result, tuple(line_points[0]), tuple(line_points[1]), (255, 0, 0), 5)

            direcao, erro = self.decisao.decide(frame, all_points, target_line, self.drive_mode)

            overlay = result.copy()
            openCV.rectangle(overlay, (10, 10), (350, 130), (0, 0, 0), -1)
            result = openCV.addWeighted(overlay, 0.6, result, 0.4, 0)
            
            openCV.putText(result, f"Status: {direcao}", (20, 40), openCV.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            openCV.putText(result, f"{erro:.1f} de erro", (20, 80), openCV.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

            cor_status = (0, 255, 0) if abs(erro) < 20 else (0, 0, 255)
            label_status = "LANE KEEPING: OK" if abs(erro) < 15 else "ALERTA: DESVIO"
            openCV.putText(result, label_status, (20, 110), openCV.FONT_HERSHEY_SIMPLEX, 0.5, cor_status, 2)

            if left_point and right_point or line_points:
                centro_cam = int((frame.shape[1] / 2))
                centro_poligono = int((left_point[1][0] + right_point[1][0]) / 2 if not line_points else line_points[1][0])
                openCV.circle(result, (centro_cam, y_max - 20), 10, (0, 0, 255), -1)
                openCV.circle(result, (centro_poligono, y_max - 20), 10, (255, 0, 0), -1)

            openCV.imshow("Navegacao Rover", result)
            openCV.imshow("ROI", roi)

            if key == ord('q'):
                break

    def cleanup(self):
        print("\nA encerrar o sistema de navegação...")
        if self.picam:
            self.picam.cleanup()
        openCV.destroyAllWindows()