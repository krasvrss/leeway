package app.leeway.bluefish;

import android.os.Bundle;
import android.webkit.WebSettings;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Android scales web text with the phone's font-size setting. Large settings
        // overflow the map controls, so follow the setting only up to 110%.
        WebSettings ws = getBridge().getWebView().getSettings();
        ws.setTextZoom(Math.min(ws.getTextZoom(), 110));
    }
}
