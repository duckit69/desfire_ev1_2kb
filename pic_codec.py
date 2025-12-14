import torch
import cv2
import numpy as np
from compressai.zoo import bmshj2018_factorized

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
            "shape": shape,
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
