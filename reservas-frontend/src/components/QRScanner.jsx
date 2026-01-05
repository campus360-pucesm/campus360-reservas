import { useEffect, useRef, useState } from "react";
import Button from "./Button";

export default function QRScanner({ onScan }) {
    const [isScanning, setIsScanning] = useState(false);
    const [status, setStatus] = useState("Inactivo");
    const qrRef = useRef(null);
    const html5QrCodeRef = useRef(null);

    useEffect(() => {
        // cleanup al desmontar
        return () => {
            stopScanner();
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const startScanner = async () => {
        if (isScanning) return;

        if (!window.Html5Qrcode) {
            setStatus("Librería de escaneo no disponible");
            return;
        }

        try {
            html5QrCodeRef.current = new window.Html5Qrcode("qr-reader");
            setStatus("Activando cámara...");

            await html5QrCodeRef.current.start(
                { facingMode: "environment" },
                { fps: 10, qrbox: { width: 250, height: 250 } },
                async (decodedText /* , decodedResult */) => {
                    setStatus(`QR detectado: ${decodedText}`);
                    await stopScanner();
                    onScan && onScan(decodedText);
                },
                () => {
                    // errores de escaneo se ignoran
                }
            );

            setIsScanning(true);
            setStatus("Cámara activa, escanea un QR de ubicación");

        } catch (err) {
            console.error(err);
            setStatus("Error al iniciar la cámara. Verifica permisos.");
            await stopScanner();
        }
    };

    const stopScanner = async () => {
        if (html5QrCodeRef.current) {
            try {
                await html5QrCodeRef.current.stop();
                await html5QrCodeRef.current.clear();
            } catch (err) {
                console.error("Error deteniendo scanner", err);
            }
        }
        html5QrCodeRef.current = null;
        setIsScanning(false);
    };

    return (
        <div>
            <div className="dashboard-section-title">Escanear ubicación</div>
            <p className="dashboard-section-subtitle">
                Usa la cámara para registrar tu acceso a laboratorios, aulas y otros espacios.
            </p>

            <div className="qr-reader-container">
                <div
                    id="qr-reader"
                    ref={qrRef}
                    style={{ width: "100%", minHeight: "260px" }}
                ></div>
            </div>

            <div style={{ marginTop: "14px", display: "flex", gap: "10px" }}>
                {!isScanning ? (
                    <Button onClick={startScanner}>📷 Abrir cámara</Button>
                ) : (
                    <Button variant="secondary" onClick={stopScanner}>
                        ❌ Detener cámara
                    </Button>
                )}
            </div>

            <p
                style={{
                    marginTop: "10px",
                    fontSize: "13px",
                    color: "#6b7280",
                }}
            >
                Estado: {status}
            </p>
        </div>
    );
}
