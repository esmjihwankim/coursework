using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GuideController : MonoBehaviour
{
    public GameObject m_Guide;
    public GameObject m_Image;


    public void Image_btn_clicked()
    {
        m_Guide.SetActive(true);
        m_Image.SetActive(true);
    }
    public void Image_back_clicked()
    {
        m_Guide.SetActive(true);
        m_Image.SetActive(false);
    }

}
