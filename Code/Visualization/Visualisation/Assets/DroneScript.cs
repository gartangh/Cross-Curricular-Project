using System;
using System.Net;
using System.Text;
using UnityEngine;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;

public class DroneScript : MonoBehaviour {
    public MqttClient client;
    public static IPAddress ip = IPAddress.Parse("157.193.214.115");
    static string position = "0,0,0";

    // message handling code
    static void client_MqttMsgPublishReceived(object sender, MqttMsgPublishEventArgs e)
    {
        position = Encoding.UTF8.GetString(e.Message);
    }

    // Use this for initialization
    void Start() {
        // port is default port dus moet niet specified worden
        // 157.193.214.115 port 1883
        client = new MqttClient(ip);
        //register to message received
        client.MqttMsgPublishReceived += client_MqttMsgPublishReceived;
        client.Connect(Guid.NewGuid().ToString());
        // subscribe to vopposition topic
        client.Subscribe(new string[] { "vopposition" }, new byte[] { 0 });
    }

    // Update is called once per frame
    void Update () {
        Vector3 coords = GetCoords(position);
        Vector3 goodcoords = TransformCoordinates(coords);
        goodcoords.y = 1;
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

    //get coordinates from a file
    Vector3 GetCoordsFromFile (string fileloc)
    {
        string position = System.IO.File.ReadAllText(fileloc);
        string[] test = position.Split(',');
        float x = float.Parse(test[0]);
        float y = float.Parse(test[1]);
        float z = float.Parse(test[2]);
        Vector3 coords = new Vector3(x, y, z);
        return coords;
    }

    Vector3 GetCoords (string position)
    {
        // coords are seperated by a comma and decimals are indicated by a dot
        string[] coord = position.Split(',');
        // unity uses comma's instead of dot's for decimals
        coord[0] = coord[0].Replace('.', ',');
        coord[1] = coord[1].Replace('.', ',');
        coord[2] = coord[2].Replace('.', ',');
        float x = float.Parse(coord[0]);
        float y = float.Parse(coord[1]);
        long z = long.Parse(coord[2]);
        Vector3 coords = new Vector3(x, y, z);
        return coords;
    }
}
