import torch
import cv2
import numpy as np
from compressai.zoo import bmshj2018_factorized
import hashlib
from typing import List, Any, Union
import json

class CardImageCodec:
    def __init__(
        self,
        quality=4,
        image_size=(128, 128),
        device=None,
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.image_size = image_size
    

        self.model = bmshj2018_factorized(
            quality=quality, pretrained=True
        ).to(self.device)
        self.model.eval()

    def _preprocess(self, path):
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, self.image_size)
        img = img / 255.0
        img = torch.tensor(img, dtype=torch.float32)
        img = img.permute(2, 0, 1).unsqueeze(0)
        return img.to(self.device)

    def compress(self, image_path):
        x = self._preprocess(image_path)

        with torch.no_grad():
            out = self.model.compress(x)

        strings = out["strings"]
        shape = out["shape"]
        # Flatten bytes
        data = strings[0][0]
        meta = {
            #"shape": shape,
            "shape": list(shape)
        }

        return data, meta

    def decompress(self, data, meta, save_path=None, show=False):
        # Rebuild strings structure expected by CompressAI
        strings = [[data]]
        shape = meta["shape"]

        with torch.no_grad():
            recon = self.model.decompress(strings, shape)["x_hat"]

        recon_img = recon.squeeze().cpu().numpy()
        recon_img = np.transpose(recon_img, (1, 2, 0))
        recon_img = (recon_img * 255).clip(0, 255).astype(np.uint8)
        recon_img = cv2.cvtColor(recon_img, cv2.COLOR_RGB2BGR)

        if save_path:
            cv2.imwrite(save_path, recon_img)

        if show:
            cv2.imshow("reconstructed", recon_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return recon_img

    def usable_compress(self, image_path):
        data, meta = self.compress(image_path)
        # Convert metadata to bytes
        meta_json = json.dumps(meta).encode('utf-8')
        meta_length = len(meta_json)

        # Total: 4 bytes (meta length) + meta + data
        total_size = 4 + meta_length + len(data)
        return total_size, data, meta




class HashManager:
    """
    A class to manage MD5 hashing operations with 16-byte output.
    """
    
    def __init__(self):
        pass
    
    def hash_list(self, data_list: List[Any], encoding: str = 'utf-8') -> bytes:
        """
        Hash a list of items using MD5.
        
        Args:
            data_list: List of items to hash
            encoding: String encoding to use (default: 'utf-8')
            
        Returns:
            16-byte MD5 hash as bytes
        """
        # Convert the entire list to a string representation
        list_string = str(data_list)
        
        # Create MD5 hash
        md5_hash = hashlib.md5()
        md5_hash.update(list_string.encode(encoding))
        
        return md5_hash.digest()  # Returns 16-byte digest
    
    def hash_string(self, text: str, encoding: str = 'utf-8') -> bytes:
        """
        Hash a string using MD5.
        
        Args:
            text: String to hash
            encoding: String encoding to use (default: 'utf-8')
            
        Returns:
            16-byte MD5 hash as bytes
        """
        md5_hash = hashlib.md5()
        md5_hash.update(text.encode(encoding))
        return md5_hash.digest()
    
    def hash_bytes(self, data: bytes) -> bytes:
        """
        Hash bytes directly using MD5.
        
        Args:
            data: Bytes to hash
            
        Returns:
            16-byte MD5 hash as bytes
        """
        md5_hash = hashlib.md5()
        md5_hash.update(data)
        return md5_hash.digest()
    
    def compare_hashes(self, hash1: bytes, hash2: bytes) -> bool:
        """
        Compare two MD5 hashes.
        
        Args:
            hash1: First hash (16 bytes)
            hash2: Second hash (16 bytes)
            
        Returns:
            True if hashes are identical, False otherwise
        """
        if len(hash1) != 16 or len(hash2) != 16:
            raise ValueError("Both hashes must be 16 bytes for MD5")
        
        return hash1 == hash2
    
    def hex_digest(self, hash_bytes: bytes) -> str:
        """
        Convert hash bytes to hexadecimal string representation.
        
        Args:
            hash_bytes: 16-byte hash
            
        Returns:
            Hexadecimal string representation
        """
        return hash_bytes.hex()
    
    def hash_list_to_hex(self, data_list: List[Any], encoding: str = 'utf-8') -> str:
        """
        Convenience method to hash a list and return hex string.
        
        Args:
            data_list: List of items to hash
            encoding: String encoding to use (default: 'utf-8')
            
        Returns:
            Hexadecimal string representation of the hash
        """
        hash_bytes = self.hash_list(data_list, encoding)
        return self.hex_digest(hash_bytes)