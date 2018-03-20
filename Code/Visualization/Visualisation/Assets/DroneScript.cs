using UnityEngine;
using uPLibrary.Networking.M2Mqtt;

public class DroneScript : MonoBehaviour {
    public MqttClient client;
    // Use this for initialization
    void Start() {
        // port is default port dus moet niet specified worden
        // 157.193.214.115 port 1883
        client = new MqttClient("157.193.214.115");
        client.Subscribe(new string[] { "vopposition" }, new byte[] { 0 });
        client.MqttMsgPublishReceived += client_MqttMsgPublishReceived;
         // dan loop starten (loop_start)
         //
	}
	
	// Update is called once per frame
	void Update () {
        Vector3 coords = GetCoordinates("position.txt");
        Vector3 goodcoords = TransformCoordinates(coords);
        transform.position = goodcoords;
	}

    // Transform coordinates to Unity coordinates
    Vector3 TransformCoordinates (Vector3 coords)
    {
        float temp = coords.y;
        coords.x /= 1000;
        coords.y = coords.z / 1000;
        coords.z = -temp / 1000;
        return coords;
    }

    Vector3 GetCoordinates (string fileloc)
    {
        string position = System.IO.File.ReadAllText(fileloc);
        string[] test = position.Split(',');
        float x = float.Parse(test[0]);
        float y = float.Parse(test[1]);
        float z = float.Parse(test[2]);
        Vector3 coords = new Vector3(x, y, z);
        return coords;
    }

}
