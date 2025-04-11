import axios from 'axios';

export class ImageTools {
    backendCompressUrl: string;
    constructor(backendCompressUrl) {
        this.backendCompressUrl = backendCompressUrl;
     }
    
    public async compressImage(file: File, targetSizeByte: number = 1*1024*1024){
        // Check if file is already smaller than target size
        if (file.size <= targetSizeByte) {
            return {
                compressedImageBlob: file,
                compressImageBase64: await this.fileToBase64(file),
                metadata: {},
                originalSize: file.size,
                compressedSize: file.size,
                compressionRatio: 0
            };
        }
    
        const formData = new FormData();
        formData.append('image', file);
        formData.append('targetSizeMB', targetSizeByte.toString());
        
        try {
            const response: AxiosResponse = await axios.post(this.backendCompressUrl, formData, 
                {
                    responseType: 'blob',
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                });
            
            // Get metadata from response headers
            const metadata = JSON.parse(response.headers['x-image-metadata'] || '{}');
            const originalSize = response.headers['x-original-size'];
            const compressedSize = response.headers['x-compressed-size'];
            /*
            exif:{
            'Exif'{
            'SubSecTimeDigitized' =
            '682054'
            'DateTimeDigitized' =
            '2022:05:05 18:05:05'
            }}
            */
            
            const base64 = await this.fileToBase64(response.data);
            
            return {
                compressedImageBlob: response.data,
                compressImageBase64: base64,
                metadata: metadata,
                originalSize: originalSize,
                compressedSize: compressedSize,
                compressionRatio: (originalSize - compressedSize) / originalSize * 100
            };
        } catch (error) {
            console.error('Error compressing image:', error);
            throw error;
        }
    }

    async fileToBase64(file: File): Promise<string> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }
}