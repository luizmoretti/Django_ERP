declare module "react-barcode-reader"{
    import React from "react";

    interface BarcodeReaderProps{
        onScan: (data: string)=> void;
        onError: (err: Error)=> void;
    }

    const BarcodeReader: React.FC<BarcodeReaderProps>;

    export default BarcodeReader;
}