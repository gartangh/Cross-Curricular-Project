using System;
using System.Net;
using System.Text;
using UnityEngine;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;

public class DroneScript : MonoBehaviour {
    public MqttClient client;
    // ip-address of mqtt server
    public static IPAddress ip = IPAddress.Parse("157.193.214.115");
    // Topics to subscribe to
    static string positionTopic = "vopposition";
    static string heightTopic = "vopheight";
    static string orientationTopic = "vopeulerangles";
    // Placeholder for updated position, height & orientation
    static string position = "29000,1000";
    static string height = "1000";
    static string orientation = "0,0,0";

    /** Message handling code */
    static void client_MqttMsgPublishReceived(object sender, MqttMsgPublishEventArgs e)
    {
        if (e.Topic.Equals(positionTopic))
        {
            position = Encoding.UTF8.GetString(e.Message);
        }
        else if (e.Topic.Equals(heightTopic))
        {
            height = Encoding.UTF8.GetString(e.Message);
        }
        else if (e.Topic.Equals(orientationTopic))
        {
            orientation = Encoding.UTF8.GetString(e.Message);
        }
    }

    /** Use this for initialization */
    void Start() {
        // Port is default port so doesnt have to be specified
        // 157.193.214.115 port 1883
        client = new MqttClient(ip);
        // Register to message received
        client.MqttMsgPublishReceived += client_MqttMsgPublishReceived;
        client.Connect(Guid.NewGuid().ToString());
        // Subscribe to vopposition, vopheight and voporientation topic
        client.Subscribe(new string[] { positionTopic, heightTopic, orientationTopic }, new byte[] { 0, 0, 0 });
    }

    /** Update is called once per frame */
    void Update () {
        // Update location
		transform.position = TransformCoordinates (GetCoords ());
        // Update orientation
		transform.rotation = GetUnityOrientation();
	}

    /** Transforms coordinates from the MQTT coordinate system to unity coordinate system */
    Vector3 TransformCoordinates(Vector3 coords)
    {
        float temp = coords.y;
        coords.y = coords.z;
        coords.z = -temp;

        return coords;
    }

    /** Gets coordinates from a string where they are as follows: "x,y,z"
     * and each decimal is indicated by a dot
     */
    Vector3 GetCoords ()
    {
        // Coords are seperated by a comma and decimals are indicated by a dot
        string[] coord = position.Split(',');
        // Unity uses comma's instead of dot's for decimals
        float x = float.Parse(coord[0].Replace('.', ','));
        float y = float.Parse(coord[1].Replace('.', ','));
        float z = float.Parse(height.Replace('.',','));

		return new Vector3(x, y, z);
    }

    /** Takes angles sent by drone and changes the rotation of the drone in unity*/
    Quaternion GetUnityOrientation()
    {
		// Angles are seperated by a comma and decimals are indicated by a dot
        string[] angles = orientation.Split(',');
		// Unity uses comma's instead of dot's for decimals
        float heading = float.Parse(angles[0].Replace('.', ','))-90;
        float roll = float.Parse(angles[1].Replace('.', ','));
        float pitch = -float.Parse(angles[2].Replace('.', ','));

		return Quaternion.Euler(roll, heading, pitch);
    }
}
