using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR;

public class Mover : MonoBehaviour
{
    private InputDevice _left_device;
    private InputDevice _right_device;
    private CharacterController _character;

    private Vector2 movement1;
    private Vector2 movement2;

    private float rotationSpeed = 20.0f;

    private Vector3 result;


    private void Start()
    {
        // assign controller to device
        _left_device = InputDevices.GetDeviceAtXRNode(XRNode.LeftHand);
        _right_device = InputDevices.GetDeviceAtXRNode(XRNode.RightHand);
        _character = GetComponent<CharacterController>();
    }

    private void Update()
    {
        _left_device.TryGetFeatureValue(CommonUsages.primary2DAxis, out movement1);
        _right_device.TryGetFeatureValue(CommonUsages.primary2DAxis, out movement2);

        // Y axis rotation is defined by x movement in controller
        float rotY = movement2.x * rotationSpeed * Mathf.Deg2Rad;
        _character.transform.Rotate(0, rotY, 0);

        Vector3 fieldMovement = new Vector3(movement1.x, y: 0, z: movement1.y) * Time.deltaTime * 1f;
        _character.Move(transform.rotation * fieldMovement);
    }

}


//float rotX = movement2.y * rotationSpeed * Mathf.Deg2Rad;
//_character.transform.Rotate(Vector3.left, rotX);
//_character.transform.Rotate(Vector3.up, rotY);