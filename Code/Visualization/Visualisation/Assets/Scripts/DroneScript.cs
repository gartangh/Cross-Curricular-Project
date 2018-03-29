using System;
using System.Net;
using System.Text;
using UnityEngine;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;

public class DroneScript : MonoBehaviour {
    public MqttClient client;
    //ip-address of mqtt server
    public static IPAddress ip = IPAddress.Parse("157.193.214.115");
    //placeholder for updated position, height & orientation
    static string position = "29000,1000";
    static string height = "1000";
    static string orientation = "0,0,0";

    // message handling code
    static void client_MqttMsgPublishReceived(object sender, MqttMsgPublishEventArgs e)
    {
        if (e.Topic.Equals("vopposition"))
        {
            position = Encoding.UTF8.GetString(e.Message);
        }
        else if (e.Topic.Equals("vopheight"))
        {
            height = Encoding.UTF8.GetString(e.Message);
        }
        else if (e.Topic.Equals("voporientation"))
        {
            orientation = Encoding.UTF8.GetString(e.Message);
        }
    }

    // Use this for initialization
    void Start() {
        // port is default port so doesnt have to be specified
        // 157.193.214.115 port 1883
        client = new MqttClient(ip);
        //register to message received
        client.MqttMsgPublishReceived += client_MqttMsgPublishReceived;
        client.Connect(Guid.NewGuid().ToString());
        // subscribe to vopposition, vopheight and voporientation topic
        client.Subscribe(new string[] { "vopposition", "vopheight", "voporientation" }, new byte[] { 0, 0, 0 });
    }

    // Update is called once per frame
    void Update () {
        Vector3 coords = GetCoords();
        Vector3 unityCoordinates = TransformCoordinates(coords);
        transform.position = unityCoordinates;
        Quaternion rotation = GetOrientation();
        transform.rotation = rotation;
	}

    /**Transforms coordinates from the MQTT coordinate system to unity coordinate system */
    Vector3 TransformCoordinates(Vector3 coords)
    {
        float temp = coords.y;
        coords.y = coords.z;
        coords.z = -temp;
        return coords;
    }

    Vector3 GetCoords ()
    {
        // coords are seperated by a comma and decimals are indicated by a dot
        string[] coord = position.Split(',');
        // unity uses comma's instead of dot's for decimals
        float x = float.Parse(coord[0].Replace('.', ','));
        float y = float.Parse(coord[1].Replace('.', ','));
        float z = float.Parse(height.Replace('.',','));
        Vector3 coords = new Vector3(x, y, z);
        return coords;
    }

    /**takes angles sent by drone and changes the rotation of the drone in unity*/
    Quaternion GetOrientation()
    {
        string[] angles = orientation.Split(',');
        float heading = float.Parse(angles[0].Replace('.', ','));
        float roll = float.Parse(angles[1].Replace('.', ','));
        float pitch = float.Parse(angles[2].Replace('.', ','));
        Quaternion quat = Quaternion.Euler(roll, heading, pitch);
        return quat;
    }
}
