from ultralytics import YOLO
import cv2
from pathlib import Path


class _DetectionModelOutput:
    def __init__(self, result, img_path):
        self.boxes: list[list[float]] = result.boxes.xywh
        self.names: list[str] = [result.names[cls.item()] for cls in result.boxes.cls.int()]
        self.confs: list[float] = result.boxes.conf

        self.result = result
        self.image_path = img_path

    def show_with_all(self):
        self.result.show()

    def show_bounds(self):
        image = cv2.imread(self.image_path)

        color = (0, 255, 0)
        for box in self.boxes:
            x, y, w, h = box
            x, y, w, h = int(x - int(w) // 2), int(y - int(h) // 2), int(w), int(h)

            thickness = 2

            cv2.rectangle(image, (x, y), (x + w, y + h), color, thickness)

        cv2.imshow("Bounding Box", image)
        cv2.waitKey()

    def __repr__(self):
        out = "(Label): (Confidence)\n--------------------\n"
        for name, conf in zip(self.names, self.confs):
            out += f"{name}: {conf:.4f}\n"

        return out


class DetectionModel:
    def __init__(self, parameter_file: str) -> None:
        self.model = YOLO(parameter_file)
        # print(self.model.__dir__())
        # exit(1)

    def predict(self, img_path):
        result = self.model(img_path)[0]
        # print(result.boxes)

        return _DetectionModelOutput(result, img_path)


if __name__ == "__main__":
    model = DetectionModel("best_the_actual_dataset.pt")
    # model = DetectionModel("/opt/homebrew/runs/detect/train80/weights/best.pt")
    # model = DetectionModel("/Users/alejansropinto/Dev/Imaging2025/yolo11n.onnx")

    result = model.predict("test_images/visdrone.jpg")
    print(len(result.confs))
    print(result.boxes)
    result.show_bounds()
    result.show_with_all()

    # Walk through images in path
    # path = Path("/Users/alejansropinto/Dev/Imaging2025/visdronestuff/VisDrone/VisDrone2019-DET-test-dev/images")
    # for i, image_path in enumerate(path.glob("*.jpg")):
    #     result = model.predict(str(image_path))
    #     confs = result.confs

    #     if len(confs) > 0:
    #         result.show_bounds()
    #         result.show_with_all()
    #         print(image_path)
    #         break
