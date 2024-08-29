import cv2
import webbrowser

qrCode = cv2.QRCodeDetector()
cap = cv2.VideoCapture(0)

if not cap.isOpened():
  print("No se puede abrir la cámara")
  exit()

while True:
    ret, frame = cap.read()

    if ret:
        ret_qr, decoded_info, points, _ = qrCode.detectAndDecodeMulti(frame)
        if ret_qr:
            for info, point in zip(decoded_info, points):
                if info:
                    color = (0, 255, 0)
                    cv2.putText(frame, info, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

                    # Verificar si es una URL y abrirla en el navegador
                    try:
                        if info.startswith('http://') or info.startswith('https://'):
                            webbrowser.open_new_tab(info)
                    except:
                        pass  # Ignorar errores al abrir el enlace

                else:
                    color = (0, 0, 255)
                frame = cv2.polylines(frame, [point.astype(int)], True, color, 8)
    else:
        print("No se puede recibir el fotograma (¿final de la transmisión?). Saliendo ...")
        break

    cv2.imshow('Detector de codigos QR', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()