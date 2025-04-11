import { ImageDescriptionViewModel } from "@/data/ImageDescriptionViewModel";

export class DuplicateFinder {
    timeThresholdMs: number;
    constructor(timeThresholdMs?: number) {
        this.timeThresholdMs = timeThresholdMs ?? 5000; // Default threshold of 5 seconds
        
    }

    /// Method to find duplicates in list of ImageDescriptionViewModel. It finds and compare the object's metadata["exif"]["0th"]["DateTime"]
    findDuplicates(images: ImageDescriptionViewModel[]): { time: number; images: ImageDescriptionViewModel[] }[] {
        // Each cluster holds a representative time and an array of images that are considered duplicates.
        const clusters: { time: number; images: ImageDescriptionViewModel[] }[] = [];

        for (const image of images) {
            if (
                image.metadata["exif"] === undefined ||
                image.metadata["exif"]["0th"] === undefined ||
                image.metadata["exif"]["0th"]["DateTime"] === undefined
            ) {
                continue; // Skip if DateTime is not available
            }
            
            // Extract and convert the DateTime from the metadata
            const dt = image.metadata["exif"]["0th"]["DateTime"];
            const dateTime = new Date(dt.replace(/^(\d{4}):(\d{2}):(\d{2})/, '$1-$2-$3').replace(' ', 'T'));
            const currentTime = dateTime.getTime();
            
            // Check if the current image's timestamp is within reasonable time of any existing cluster
            let clusterFound = false;
            for (const cluster of clusters) {
                if (Math.abs(cluster.time - currentTime) <= this.timeThresholdMs) {
                    cluster.images.push(image);
                    clusterFound = true;
                    break;
                }
            }
            
            // If no matching cluster is found, create a new one
            if (!clusterFound) {
                clusters.push({ time: currentTime, images: [image] });
            }
        }
        
        // Flatten out clusters that have more than one image (duplicates).
        const duplicates: ImageDescriptionViewModel[] = [];
        for (const cluster of clusters) {
            if (cluster.images.length > 1) {
                // Ensure images are not added twice if they already appear in the duplicates array.
                for (const img of cluster.images) {
                    if (!duplicates.includes(img)) {
                        duplicates.push(img);
                    }
                }
            }
        }
        
        return clusters.filter(x=>x.images.length>1); // Return duplicates only if any cluster has more than one image.
    }
}